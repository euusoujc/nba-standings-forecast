"""Versões da previsão com 0, 5, 10 e 15 jogos disputados.

Cada versão refaz o pipeline inteiro como se estivéssemos no dia em que o último
time completou N jogos em 2026-27:
  - features com os N primeiros jogos (V0: só a temporada anterior, pré-temporada);
  - Ridge com validação leave-one-season-out;
  - modelo de jogo e sigma ajustados com os jogos após o N-ésimo;
  - backtest fora da amostra nas 16 temporadas históricas;
  - Monte Carlo de 2026-27: campanha até a data de corte + todos os jogos depois dela
    (os já disputados depois da data contam como "ainda não jogados").

V15 coincide com a simulação principal (simulacao.py).
O projeto é "vivo": rodando `python src/coleta.py --refresh-current` e o pipeline de
novo, N passa a ser o número de jogos do dia e uma nova versão pode ser acrescentada.

Uso: python src/versoes.py   (depois de simulacao.py)
"""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge

try:
    from config import PROCESSED, RESULTS, CURRENT_SEASON, HIST_SEASONS, CONFERENCE
    from features import build_features, FEATURES, _prev_season_pct
    from modelos import Tuned, _pipe, ALPHAS_RIDGE, mae_wins, spearman_conf, TARGET
    from simulacao import (game_training_set, fit_game_model, rating_sigma, simulate,
                           summarize_sims, backtest, cutoff_date, GAMES_TARGET)
    from i18n import L, LANGS, fig_path
except ImportError:
    from src.config import PROCESSED, RESULTS, CURRENT_SEASON, HIST_SEASONS, CONFERENCE
    from src.features import build_features, FEATURES, _prev_season_pct
    from src.modelos import Tuned, _pipe, ALPHAS_RIDGE, mae_wins, spearman_conf, TARGET
    from src.simulacao import (game_training_set, fit_game_model, rating_sigma, simulate,
                               summarize_sims, backtest, cutoff_date, GAMES_TARGET)
    from src.i18n import L, LANGS, fig_path

VERSIONS = [0, 5, 10, 15]


class RidgeOn(Tuned):
    """Ridge (alpha por CV agrupada + regra de 1 EP) sobre uma lista de features."""
    def __init__(self, feats):
        super().__init__(_pipe(Ridge()), {"model__alpha": ALPHAS_RIDGE})
        self.feats = feats

    def fit(self, X, y, groups):
        return super().fit(X[self.feats], y, groups)

    def predict(self, X):
        return super().predict(X[self.feats])


def features_at(games: pd.DataFrame, n: int) -> pd.DataFrame:
    if n > 0:
        return build_features(games, n)
    f = games.groupby(["SEASON", "TEAM"]).agg(final_gp=("WIN", "size"),
                                              final_win_pct=("WIN", "mean")).reset_index()
    f = f.merge(_prev_season_pct(games), on=["SEASON", "TEAM"], how="left")
    f.loc[f.SEASON == CURRENT_SEASON, "final_win_pct"] = np.nan
    f["gp"] = 0; f["wins"] = 0
    f["CONF"] = f.TEAM.map(CONFERENCE)
    return f


def run_version(games, rem, n):
    feats = features_at(games, n)
    hist = feats[feats.SEASON.isin(HIST_SEASONS)].reset_index(drop=True)
    cur = feats[feats.SEASON == CURRENT_SEASON].reset_index(drop=True)
    cols = ["prev_win_pct"] if n == 0 else FEATURES
    base_col = "prev_win_pct" if n == 0 else "win_pct"

    # LOSO (ratings fora da amostra)
    loso = hist[["SEASON", "TEAM", "CONF", TARGET]].copy()
    loso["rating"] = np.nan
    for s in hist.SEASON.unique():
        tr, te = hist.SEASON != s, hist.SEASON == s
        m = RidgeOn(cols).fit(hist[tr], hist.loc[tr, TARGET], hist.loc[tr, "SEASON"])
        loso.loc[te, "rating"] = m.predict(hist[te])
    loso["base"] = hist[base_col]

    hgames = games[games.SEASON != CURRENT_SEASON]
    train = game_training_set(hgames, loso, n)
    coef = fit_game_model(train).coef_[0]
    sigma = rating_sigma(loso, "rating", n)
    bt, brier, brier_ref, cover = backtest(games, loso, "rating", train, n)

    # 2026-27 a partir da data de corte
    c = games[games.SEASON == CURRENT_SEASON].sort_values(["TEAM", "GAME_DATE", "GAME_ID"]).copy()
    c["k"] = c.groupby("TEAM").cumcount() + 1
    cut = cutoff_date(c, n)
    m = RidgeOn(cols).fit(hist, hist[TARGET], hist["SEASON"])
    cur["rating"] = m.predict(cur)
    teams = cur.TEAM.to_numpy(); conf = cur.CONF.to_numpy()
    tix = {t: i for i, t in enumerate(teams)}
    known = c[c.GAME_DATE <= cut]
    cur_w = known.groupby("TEAM")["WIN"].sum().reindex(teams).fillna(0).to_numpy()
    cur_gp = known.groupby("TEAM").size().reindex(teams).fillna(0).astype(int).to_numpy()
    later = c[(c.GAME_DATE > cut) & (c.HOME == 1)]
    h = np.concatenate([later.TEAM.map(tix).to_numpy(), rem.HOME.map(tix).to_numpy()]).astype(int)
    a = np.concatenate([later.OPP.map(tix).to_numpy(), rem.AWAY.map(tix).to_numpy()]).astype(int)
    sched = np.bincount(np.concatenate([h, a]), minlength=len(teams))
    extra = GAMES_TARGET - cur_gp - sched
    wins, pos = simulate(teams, conf, cur.rating.to_numpy(), cur_w, cur_gp, h, a, coef, sigma,
                         extra_games=extra)
    summ = summarize_sims(teams, conf, wins, pos, cur_gp + sched + extra)
    summ.insert(2, "V_atual", cur_w.astype(int)); summ.insert(3, "D_atual", cur_gp - cur_w.astype(int))
    summ.insert(4, "rating", cur.rating.to_numpy())
    summ.insert(0, "N", n)

    mae_bt = float(np.mean(np.abs(bt.vitorias_esperadas - bt.real_wins)))
    row = {"versao": f"V{n}", "N": n, "data_corte": str(pd.Timestamp(cut).date()),
           "jogos_no_corte": f"{cur_gp.min()}-{cur_gp.max()}",
           "MAE_LOSO_baseline": mae_wins(loso[TARGET], loso.base),
           "MAE_LOSO_ridge": mae_wins(loso[TARGET], loso.rating),
           "Spearman_LOSO_ridge": spearman_conf(loso, "rating"),
           "sigma": sigma, "b_diff": coef[0], "b_casa": coef[1],
           "brier_backtest": brier, "brier_referencia": brier_ref,
           "cobertura_ic80": cover, "MAE_backtest_vitorias": mae_bt}
    print(f"V{n:<2d} corte {row['data_corte']} ({row['jogos_no_corte']} jogos): "
          f"MAE LOSO {row['MAE_LOSO_baseline']:.2f} -> {row['MAE_LOSO_ridge']:.2f}; "
          f"sigma {sigma:.3f}; Brier {brier:.3f}; cobertura {cover:.1%}; MAE backtest {mae_bt:.2f}")
    return row, summ


def plot_trajectories(long, lang):
    t = L[lang]
    fig, axes = plt.subplots(1, 2, figsize=(16, 8.5), sharey=True)
    cmap = plt.get_cmap("tab20")
    for ax, cf in zip(axes, ["Leste", "Oeste"]):
        d = long[long.CONF == cf]
        last = d[d.N == d.N.max()].sort_values("vitorias_esperadas", ascending=False)
        # rótulos sem sobreposição: desce cada um até ficar a >= 1,1 vitória do anterior
        ys = last.vitorias_esperadas.to_numpy().copy()
        for j in range(1, len(ys)):
            ys[j] = min(ys[j], ys[j - 1] - 1.1)
        for i, (tm, yl) in enumerate(zip(last.TEAM, ys)):
            x = d[d.TEAM == tm].sort_values("N")
            ax.plot(x.N, x.vitorias_esperadas, "o-", lw=2, ms=5, color=cmap(i % 20))
            ax.annotate(tm, (x.N.iloc[-1], x.vitorias_esperadas.iloc[-1]), xytext=(x.N.iloc[-1] + 0.7, yl),
                        textcoords="data", va="center", fontsize=10, color=cmap(i % 20))
        ax.set_xticks(sorted(d.N.unique())); ax.set_xticklabels([f"V{v}" for v in sorted(d.N.unique())])
        ax.set_xlabel(t["ver_x"]); ax.set_title(t["conf"].format(c=t[cf])); ax.grid(alpha=0.3)
        ax.set_xlim(-1, d.N.max() + 2.5)
    axes[0].set_ylabel(t["ver_y"])
    fig.suptitle(t["ver_title"], fontsize=16)
    fig.savefig(fig_path("versoes_trajetoria.png", lang)); plt.close(fig)


def plot_metrics(res, lang):
    t = L[lang]
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    axes[0].plot(res.N, res.brier_backtest, "o-", color="#1f6fb4", lw=2.5, ms=8)
    axes[0].axhline(res.brier_referencia.iloc[0], color="#999999", ls="--", lw=1.5)
    axes[0].set_ylabel(t["ver_brier"])
    axes[1].plot(res.N, res.MAE_backtest_vitorias, "o-", color="#c0392b", lw=2.5, ms=8)
    axes[1].set_ylabel(t["ver_mae"])
    for ax in axes:
        ax.set_xticks(res.N); ax.set_xticklabels([f"V{v}" for v in res.N])
        ax.set_xlabel(t["ver_x"]); ax.grid(alpha=0.3)
    fig.suptitle(t["ver_metric_title"], fontsize=15)
    fig.tight_layout()
    fig.savefig(fig_path("versoes_backtest.png", lang)); plt.close(fig)


def main():
    games = pd.read_csv(PROCESSED / "games.csv", dtype={"GAME_ID": str}, parse_dates=["GAME_DATE"])
    games["GAME_ID"] = games["GAME_ID"].str.zfill(10)
    rem = pd.read_csv(PROCESSED / "remaining_2026-27.csv", dtype={"GAME_ID": str})
    rows, sims = [], []
    for n in VERSIONS:
        r, s = run_version(games, rem, n)
        rows.append(r); sims.append(s)
    res = pd.DataFrame(rows)
    long = pd.concat(sims, ignore_index=True)
    res.round(4).to_csv(RESULTS / "versoes_resumo.csv", index=False)
    long.round(3).to_csv(RESULTS / "versoes_2026-27.csv", index=False)
    for lang in LANGS:
        plot_trajectories(long, lang)
        plot_metrics(res, lang)

    wide = long.pivot(index=["CONF", "TEAM"], columns="N", values="vitorias_esperadas").round(1)
    wide.columns = [f"V{c}" for c in wide.columns]
    print("\nVitórias esperadas por versão:")
    print(wide.sort_values(["CONF", f"V{VERSIONS[-1]}"], ascending=[True, False]).to_string())


if __name__ == "__main__":
    main()
