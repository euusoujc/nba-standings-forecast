"""Fase 4 - Simulação Monte Carlo do restante da temporada 2026-27.

1. Rating de cada time = aproveitamento final previsto pelo melhor modelo da fase 3.
   No histórico usamos as previsões LOSO (fora da amostra), para não vazar.
2. Modelo de jogo: regressão logística
       logit P(time vence) = b_diff * (rating_time - rating_adv) + b_casa * mando
   com mando = +1 em casa e -1 fora (sem intercepto, por simetria), treinada nos
   jogos históricos disputados DEPOIS do N-ésimo jogo de ambos os times.
3. Incerteza do rating: em cada simulação o rating de cada time recebe um ruído
   N(0, sigma), com sigma estimado dos resíduos LOSO descontando a variância
   binomial dos jogos restantes.
4. Monte Carlo (10.000 vezes): vitórias atuais + jogos restantes do calendário
   + 2 jogos da NBA Cup ainda não definidos (contra um adversário médio, quadra neutra).
5. Desempate: aleatório (limitação documentada).

Uso: python src/simulacao.py
"""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

try:
    from config import PROCESSED, RESULTS, FIGURES, SEED, CURRENT_SEASON
    from modelos import fit_final, TARGET
    from i18n import L, LANGS, fig_path
except ImportError:
    from src.config import PROCESSED, RESULTS, FIGURES, SEED, CURRENT_SEASON
    from src.modelos import fit_final, TARGET
    from src.i18n import L, LANGS, fig_path

N_SIMS = 10_000
GAMES_TARGET = 82
plt.rcParams.update({"font.size": 13, "savefig.dpi": 200, "savefig.bbox": "tight"})


# ------------------------------------------------------------ modelo de jogo
def game_training_set(games: pd.DataFrame, ratings: pd.DataFrame, n: int) -> pd.DataFrame:
    """Uma linha por time-jogo, apenas jogos após o N-ésimo jogo de ambos os times."""
    g = games.sort_values(["SEASON", "TEAM", "GAME_DATE", "GAME_ID"]).copy()
    g["k"] = g.groupby(["SEASON", "TEAM"]).cumcount() + 1
    kopp = g[["GAME_ID", "TEAM", "k"]].rename(columns={"TEAM": "OPP", "k": "k_opp"})
    g = g.merge(kopp, on=["GAME_ID", "OPP"])
    g = g[(g.k > n) & (g.k_opp > n)]
    r = ratings[["SEASON", "TEAM", "rating"]]
    g = g.merge(r, on=["SEASON", "TEAM"]).merge(
        r.rename(columns={"TEAM": "OPP", "rating": "rating_opp"}), on=["SEASON", "OPP"])
    g["diff"] = g["rating"] - g["rating_opp"]
    g["mando"] = np.where(g["HOME"] == 1, 1.0, -1.0)
    return g


def fit_game_model(train: pd.DataFrame) -> LogisticRegression:
    lr = LogisticRegression(fit_intercept=False, C=1e6)
    lr.fit(train[["diff", "mando"]], train["WIN"])
    return lr


def rating_sigma(loso: pd.DataFrame, pred_col: str, n: int) -> float:
    """Desvio do 'talento' não explicado pelo modelo.

    Var(resíduo do aproveitamento final) = f^2 * sigma^2 + Var(sorte binomial),
    com f = fração de jogos restantes. Resolve para sigma.
    """
    resid = loso[TARGET] - loso[pred_col]
    f = (GAMES_TARGET - n) / GAMES_TARGET
    luck = (loso[TARGET] * (1 - loso[TARGET])).mean() * (GAMES_TARGET - n) / GAMES_TARGET ** 2
    return float(np.sqrt(max(resid.var() - luck, 1e-6)) / f)


# ------------------------------------------------------------ Monte Carlo
def simulate(teams, conf, rating, cur_wins, cur_gp, home_idx, away_idx, coef,
             sigma, n_sims=N_SIMS, extra_games=None, seed=SEED):
    """Retorna (vitórias finais [sims x times], posição na conferência [sims x times])."""
    rng = np.random.default_rng(seed)
    b_diff, b_home = coef
    T = len(teams)
    r = rating[None, :] + rng.normal(0, sigma, size=(n_sims, T))   # incerteza do rating
    wins = np.repeat(cur_wins[None, :].astype(float), n_sims, axis=0)

    if len(home_idx):
        logit = b_diff * (r[:, home_idx] - r[:, away_idx]) + b_home
        home_win = rng.random(logit.shape) < 1 / (1 + np.exp(-logit))
        np.add.at(wins.T, home_idx, home_win.T)   # soma por time (eixo dos times)
        np.add.at(wins.T, away_idx, (~home_win).T)

    if extra_games is not None:  # jogos ainda não marcados: adversário médio, neutro
        logit = b_diff * (r - 0.5)
        p = 1 / (1 + np.exp(-logit))
        wins += rng.binomial(extra_games[None, :].repeat(n_sims, 0), p)

    # Classificação por conferência, desempate aleatório
    key = wins + rng.random(wins.shape) * 1e-3
    pos = np.zeros_like(wins, dtype=int)
    for c in np.unique(conf):
        idx = np.where(conf == c)[0]
        order = np.argsort(-key[:, idx], axis=1)
        ranks = np.empty_like(order)
        np.put_along_axis(ranks, order, np.arange(1, len(idx) + 1)[None, :].repeat(n_sims, 0), axis=1)
        pos[:, idx] = ranks
    return wins, pos


def summarize_sims(teams, conf, wins, pos, total_games):
    df = pd.DataFrame({
        "TEAM": teams, "CONF": conf,
        "vitorias_esperadas": wins.mean(0),
        "IC80_inf": np.percentile(wins, 10, axis=0),
        "IC80_sup": np.percentile(wins, 90, axis=0),
        "P_top6": (pos <= 6).mean(0),
        "P_playin": ((pos >= 7) & (pos <= 10)).mean(0),
        "P_fora": (pos >= 11).mean(0),
        "posicao_media": pos.mean(0),
    })
    df["jogos"] = total_games
    return df


# ------------------------------------------------------------ backtest
def backtest(games, loso, pred_col, train, n, n_sims=2000):
    """Simula cada temporada histórica como se estivéssemos no dia em que o último
    time completou N jogos (mesma situação de 2026-27) e compara com o real.

    Totalmente fora da amostra: o rating vem das previsões LOSO, e o modelo de jogo
    e o sigma são reajustados SEM a temporada testada.
    """
    rows = []
    for season, sl in loso.groupby("SEASON"):
        g = games[games.SEASON == season].sort_values(["TEAM", "GAME_DATE", "GAME_ID"]).copy()
        g["k"] = g.groupby("TEAM").cumcount() + 1
        cut = g.loc[g.k == n, "GAME_DATE"].max()          # data de corte
        teams = sl.TEAM.to_numpy()
        tix = {t: i for i, t in enumerate(teams)}
        known = g[g.GAME_DATE <= cut]
        cur_w = known.groupby("TEAM")["WIN"].sum().reindex(teams).fillna(0).to_numpy()
        rest = g[(g.GAME_DATE > cut) & (g.HOME == 1)]
        h = rest.TEAM.map(tix).to_numpy(); a = rest.OPP.map(tix).to_numpy()

        coef = fit_game_model(train[train.SEASON != season]).coef_[0]
        sigma = rating_sigma(loso[loso.SEASON != season], pred_col, n)
        wins, pos = simulate(teams, sl.CONF.to_numpy(), sl[pred_col].to_numpy(), cur_w, None,
                             h, a, coef, sigma, n_sims=n_sims, seed=SEED)
        s = summarize_sims(teams, sl.CONF.to_numpy(), wins, pos, None)
        real = g.groupby("TEAM").agg(w=("WIN", "sum"), pct=("WIN", "mean")).reindex(teams)
        s["real_wins"] = real.w.to_numpy()
        s["real_pos"] = (real.assign(CONF=sl.CONF.to_numpy())
                         .groupby("CONF")["pct"].rank(ascending=False, method="first").to_numpy())
        s["SEASON"] = season
        s["gp_corte_min"] = known.groupby("TEAM").size().min()
        s["gp_corte_max"] = known.groupby("TEAM").size().max()
        rows.append(s)
    bt = pd.concat(rows, ignore_index=True)
    y6 = (bt.real_pos <= 6).astype(float)
    ypi = ((bt.real_pos >= 7) & (bt.real_pos <= 10)).astype(float)
    yout = (bt.real_pos >= 11).astype(float)
    brier = np.mean((bt.P_top6 - y6) ** 2 + (bt.P_playin - ypi) ** 2 + (bt.P_fora - yout) ** 2)
    # referência: probabilidades históricas constantes (6/15, 4/15, 5/15)
    brier_ref = np.mean((6 / 15 - y6) ** 2 + (4 / 15 - ypi) ** 2 + (5 / 15 - yout) ** 2)
    cover = np.mean((bt.real_wins >= bt.IC80_inf) & (bt.real_wins <= bt.IC80_sup))
    return bt, brier, brier_ref, cover


# ------------------------------------------------------------ gráficos
def plot_heatmaps(teams, conf, pos, summ, lang):
    t = L[lang]
    fig, axes = plt.subplots(1, 2, figsize=(18, 8.5))
    for ax, c in zip(axes, ["Leste", "Oeste"]):
        idx = np.where(conf == c)[0]
        order = idx[np.argsort(summ.loc[idx, "posicao_media"].to_numpy())]
        M = np.stack([(pos[:, i][:, None] == np.arange(1, 16)[None, :]).mean(0) for i in order])
        im = ax.imshow(M * 100, cmap="Blues", vmin=0, vmax=max(60, M.max() * 100), aspect="auto")
        for i in range(M.shape[0]):
            for j in range(M.shape[1]):
                v = M[i, j] * 100
                if v >= 1:
                    ax.text(j, i, f"{v:.0f}", ha="center", va="center", fontsize=9,
                            color="white" if v > 35 else "black")
        ax.set_yticks(range(len(order))); ax.set_yticklabels(teams[order])
        ax.set_xticks(range(15)); ax.set_xticklabels(range(1, 16))
        ax.axvline(5.5, color="#c0392b", lw=2); ax.axvline(9.5, color="#c0392b", lw=2, ls="--")
        ax.set_xlabel(t["position"]); ax.set_title(t["conf"].format(c=t[c]))
    fig.colorbar(im, ax=axes, shrink=0.8, label=t["prob_pct"])
    sims = f"{N_SIMS:,}".replace(",", "." if lang == "pt" else ",")
    fig.suptitle(t["heat_title"].format(sims=sims), fontsize=17)
    fig.savefig(fig_path("heatmap_posicoes.png", lang)); plt.close(fig)


def plot_probs(summ, lang):
    t = L[lang]
    fig, axes = plt.subplots(1, 2, figsize=(16, 7.5), sharex=True)
    for ax, c in zip(axes, ["Leste", "Oeste"]):
        d = summ[summ.CONF == c].sort_values("vitorias_esperadas")
        y = np.arange(len(d))
        ax.barh(y, d.P_top6 * 100, color="#1f6fb4", label=t["top6"])
        ax.barh(y, d.P_playin * 100, left=d.P_top6 * 100, color="#f0a202", label=t["playin"])
        ax.barh(y, d.P_fora * 100, left=(d.P_top6 + d.P_playin) * 100, color="#bbbbbb", label=t["out"])
        ax.set_yticks(y)
        ax.set_yticklabels([f"{tm}  ({w:.0f}{t['W']})" for tm, w in zip(d.TEAM, d.vitorias_esperadas)])
        ax.set_xlim(0, 100); ax.set_xlabel(t["prob_pct"]); ax.set_title(t["conf"].format(c=t[c]))
    axes[0].legend(loc="lower right", fontsize=11)
    fig.subplots_adjust(wspace=0.35)
    fig.suptitle(t["probs_title"], fontsize=16)
    fig.savefig(fig_path("probabilidades_top6_playin.png", lang)); plt.close(fig)


def calibration_table(bt, bins=np.linspace(0, 1, 11)):
    """Probabilidade prevista x frequência observada, juntando as 3 classes."""
    rows = []
    for col, ok in [("P_top6", bt.real_pos <= 6),
                    ("P_playin", (bt.real_pos >= 7) & (bt.real_pos <= 10)),
                    ("P_fora", bt.real_pos >= 11)]:
        rows.append(pd.DataFrame({"p": bt[col], "y": ok.astype(float), "classe": col}))
    d = pd.concat(rows)
    d["bin"] = pd.cut(d.p, bins, include_lowest=True)
    return d.groupby("bin", observed=True).agg(p=("p", "mean"), y=("y", "mean"), n=("y", "size")).reset_index()


def plot_calibration(cal, lang):
    t = L[lang]
    fig, ax = plt.subplots(figsize=(7.5, 7))
    ax.plot([0, 1], [0, 1], "k--", lw=1, label=t["perfect"])
    ax.plot(cal.p, cal.y, "o-", color="#1f6fb4", lw=2.5, ms=8, label="Monte Carlo")
    for _, r in cal.iterrows():
        ax.annotate(f"n={r.n}", (r.p, r.y), textcoords="offset points", xytext=(6, -14), fontsize=9,
                    color="grey")
    ax.set_xlabel(t["calib_x"]); ax.set_ylabel(t["calib_y"]); ax.set_title(t["calib_title"])
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.grid(alpha=0.3); ax.legend(loc="upper left")
    fig.savefig(fig_path("calibracao_simulacao.png", lang)); plt.close(fig)


# ------------------------------------------------------------ main
def main():
    games = pd.read_csv(PROCESSED / "games.csv", dtype={"GAME_ID": str}, parse_dates=["GAME_DATE"])
    games["GAME_ID"] = games["GAME_ID"].str.zfill(10)
    hist = pd.read_csv(PROCESSED / "features_hist.csv")
    cur = pd.read_csv(PROCESSED / "features_2026-27.csv")
    rem = pd.read_csv(PROCESSED / "remaining_2026-27.csv", dtype={"GAME_ID": str})
    loso = pd.read_csv(RESULTS / "predicoes_loso.csv")
    best = (RESULTS / "melhor_modelo.txt").read_text(encoding="utf-8").strip()
    n = int(cur.gp.iloc[0])

    # 1) modelo de jogo com ratings LOSO (fora da amostra)
    ratings_hist = loso.rename(columns={best: "rating"})
    train = game_training_set(games[games.SEASON != CURRENT_SEASON], ratings_hist, n)
    gm = fit_game_model(train)
    coef = gm.coef_[0]
    p_hat = gm.predict_proba(train[["diff", "mando"]])[:, 1]
    acc = ((p_hat > 0.5) == train.WIN).mean()
    ll = -np.mean(train.WIN * np.log(p_hat) + (1 - train.WIN) * np.log(1 - p_hat))
    sigma = rating_sigma(loso, best, n)
    p_home = 1 / (1 + np.exp(-coef[1]))
    print(f"Modelo de jogo ({len(train)} linhas time-jogo): b_diff = {coef[0]:.3f}, "
          f"b_casa = {coef[1]:.3f} -> P(vitória em casa, times iguais) = {p_home:.3f}")
    print(f"  acurácia = {acc:.3f}, log-loss = {ll:.4f}; sigma do rating = {sigma:.3f}")

    # 2) backtest nas temporadas históricas (fora da amostra)
    bt, brier, brier_ref, cover = backtest(games, loso, best, train, n)
    bt.to_csv(RESULTS / "backtest_simulacao.csv", index=False)
    cal = calibration_table(bt)
    cal.to_csv(RESULTS / "calibracao_simulacao.csv", index=False)
    for lang in LANGS:
        plot_calibration(cal, lang)
    print(f"Backtest 16 temporadas (corte na data em que o último time completa {n} jogos; "
          f"times com {bt.gp_corte_min.min()}-{bt.gp_corte_max.max()} jogos no corte):")
    print(f"  Brier (3 classes) = {brier:.3f} vs {brier_ref:.3f} da referência constante; "
          f"cobertura do IC80 de vitórias = {cover:.1%}")

    pd.Series({"linhas_treino": len(train), "b_diff": coef[0], "b_casa": coef[1],
               "p_casa_times_iguais": p_home, "acuracia": acc, "log_loss": ll, "sigma_rating": sigma,
               "brier_backtest": brier, "brier_referencia": brier_ref, "cobertura_ic80": cover}
              ).to_csv(RESULTS / "modelo_jogo.csv", header=["valor"])

    # 3) simulação 2026-27
    m = fit_final(best, hist)
    cur["rating"] = m.predict(cur)
    teams = cur.TEAM.to_numpy(); conf = cur.CONF.to_numpy()
    tix = {t: i for i, t in enumerate(teams)}
    played = games[games.SEASON == CURRENT_SEASON]
    cur_w = played.groupby("TEAM")["WIN"].sum().reindex(teams).to_numpy()
    cur_gp = played.groupby("TEAM").size().reindex(teams).to_numpy()
    h = rem.HOME.map(tix).to_numpy(); a = rem.AWAY.map(tix).to_numpy()
    sched_ct = np.bincount(np.concatenate([h, a]), minlength=len(teams))
    extra = GAMES_TARGET - cur_gp - sched_ct
    print(f"2026-27: {len(rem)} jogos restantes no calendário; jogos extras (Cup, a definir) "
          f"por time: {sorted(set(extra.tolist()))}")

    wins, pos = simulate(teams, conf, cur.rating.to_numpy(), cur_w, cur_gp, h, a, coef, sigma,
                         extra_games=extra)
    summ = summarize_sims(teams, conf, wins, pos, cur_gp + sched_ct + extra)
    summ.insert(2, "V_atual", cur_w); summ.insert(3, "D_atual", cur_gp - cur_w)
    summ.insert(4, "rating", cur.rating.to_numpy())
    summ = summ.sort_values(["CONF", "posicao_media"])
    summ.round(3).to_csv(RESULTS / "simulacao_2026-27.csv", index=False)
    by_idx = summ.reset_index(drop=True).set_index(summ.TEAM.map(tix).to_numpy()).sort_index()
    for lang in LANGS:
        plot_heatmaps(teams, conf, pos, by_idx, lang)
        plot_probs(summ, lang)

    show = summ.copy()
    for col in ["P_top6", "P_playin", "P_fora"]:
        show[col] = (show[col] * 100).round(1)
    show["IC80"] = show.IC80_inf.round(0).astype(int).astype(str) + "-" + show.IC80_sup.round(0).astype(int).astype(str)
    print(show[["CONF", "TEAM", "V_atual", "D_atual", "vitorias_esperadas", "IC80",
                "P_top6", "P_playin", "P_fora"]].round(1).to_string(index=False))


if __name__ == "__main__":
    main()
