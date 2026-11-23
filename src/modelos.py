"""Fase 3 - Modelos, validação e comparação.

Baselines: (a) mantém o aproveitamento atual; (b) Pythagorean expectation.
Modelos: Regressão Linear, Ridge, Lasso (alpha via CV interna agrupada por
temporada) e Random Forest, todos com StandardScaler dentro do Pipeline.
Validação: leave-one-season-out (LOSO) e holdout temporal
(treino 2010-11..2022-23, teste 2023-24..2025-26).
Métricas: MAE em vitórias (escala 82 jogos) e Spearman médio da
classificação prevista x real por conferência.

Uso: python src/modelos.py
"""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Lasso, LinearRegression, Ridge
from sklearn.model_selection import GridSearchCV, GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

try:
    from config import PROCESSED, RESULTS, FIGURES, SEED, HIST_SEASONS
    from features import FEATURES
    from i18n import L, LANGS, fig_path
except ImportError:
    from src.config import PROCESSED, RESULTS, FIGURES, SEED, HIST_SEASONS
    from src.features import FEATURES
    from src.i18n import L, LANGS, fig_path

TARGET = "final_win_pct"
TRAIN_HOLDOUT = HIST_SEASONS[:13]   # 2010-11 .. 2022-23
TEST_HOLDOUT = HIST_SEASONS[13:]    # 2023-24 .. 2025-26
ALPHAS_RIDGE = np.logspace(-3, 3, 25)
ALPHAS_LASSO = np.logspace(-5, -0.5, 25)

plt.rcParams.update({"font.size": 14, "axes.titlesize": 16, "axes.labelsize": 14,
                     "figure.dpi": 110, "savefig.dpi": 200, "savefig.bbox": "tight"})


# ---------------------------------------------------------------- modelos
class Baseline:
    """Usa uma coluna como previsão direta (sem treino)."""
    def __init__(self, col):
        self.col = col

    def fit(self, X, y, groups=None):
        return self

    def predict(self, X):
        return X[self.col].to_numpy()


def _one_se_rule(cv_results):
    """Maior alpha cujo erro de CV está a até 1 erro-padrão do mínimo.

    Assume a grade de alphas em ordem crescente (mais regularização = mais simples).
    A curva de CV é quase plana para alphas pequenos; a regra de 1 EP escolhe o
    modelo mais encolhido que é estatisticamente indistinguível do melhor.
    """
    err = -cv_results["mean_test_score"]
    n_splits = sum(k.startswith("split") and k.endswith("_test_score") for k in cv_results)
    se = cv_results["std_test_score"] / np.sqrt(n_splits)
    best = int(np.argmin(err))
    ok = np.where(err <= err[best] + se[best])[0]
    return int(ok.max())


class Tuned:
    """GridSearchCV com GroupKFold por temporada (CV interna, sem vazamento entre anos)
    e escolha do alpha pela regra de 1 erro-padrão."""
    def __init__(self, estimator, param_grid, n_splits=5):
        self.estimator, self.param_grid, self.n_splits = estimator, param_grid, n_splits

    def fit(self, X, y, groups):
        n = min(self.n_splits, len(np.unique(groups)))
        self.gs_ = GridSearchCV(self.estimator, self.param_grid, cv=GroupKFold(n),
                                scoring="neg_mean_absolute_error", refit=_one_se_rule)
        self.gs_.fit(X, y, groups=groups)
        return self

    def predict(self, X):
        return self.gs_.predict(X)

    @property
    def best_estimator_(self):
        return self.gs_.best_estimator_


class Plain:
    def __init__(self, estimator):
        self.estimator = estimator

    def fit(self, X, y, groups=None):
        self.estimator.fit(X[FEATURES], y)
        return self

    def predict(self, X):
        return self.estimator.predict(X[FEATURES])


def _pipe(model):
    return Pipeline([("scaler", StandardScaler()), ("model", model)])


class _OnFeatures(Tuned):
    def fit(self, X, y, groups):
        return super().fit(X[FEATURES], y, groups)

    def predict(self, X):
        return super().predict(X[FEATURES])


def make_models():
    return {
        "Baseline: aproveitamento atual": lambda: Baseline("win_pct"),
        "Baseline: Pythagorean": lambda: Baseline("pyth"),
        "Regressão Linear": lambda: Plain(_pipe(LinearRegression())),
        "Ridge": lambda: _OnFeatures(_pipe(Ridge()), {"model__alpha": ALPHAS_RIDGE}),
        "Lasso": lambda: _OnFeatures(_pipe(Lasso(max_iter=50_000)), {"model__alpha": ALPHAS_LASSO}),
        "Random Forest": lambda: Plain(_pipe(RandomForestRegressor(
            n_estimators=500, min_samples_leaf=10, max_features=0.5,
            random_state=SEED, n_jobs=-1))),
    }


# ---------------------------------------------------------------- métricas
def mae_wins(y, p):
    return float(np.mean(np.abs(np.asarray(y) - np.asarray(p))) * 82)


def spearman_conf(df, pred_col, true_col=TARGET):
    """Spearman médio entre classificação prevista e real, por (temporada, conferência)."""
    vals = [spearmanr(g[pred_col], g[true_col]).statistic
            for _, g in df.groupby(["SEASON", "CONF"])]
    return float(np.mean(vals))


# ---------------------------------------------------------------- validação
def loso_predictions(df, models):
    out = df[["SEASON", "TEAM", "CONF", TARGET, "win_pct"]].copy()
    for name, make in models.items():
        out[name] = np.nan
        for s in df.SEASON.unique():
            tr, te = df.SEASON != s, df.SEASON == s
            m = make().fit(df[tr], df.loc[tr, TARGET], groups=df.loc[tr, "SEASON"])
            out.loc[te, name] = m.predict(df[te])
    return out


def holdout_predictions(df, models):
    tr = df[df.SEASON.isin(TRAIN_HOLDOUT)]
    te = df[df.SEASON.isin(TEST_HOLDOUT)]
    out = te[["SEASON", "TEAM", "CONF", TARGET, "win_pct"]].copy()
    for name, make in models.items():
        m = make().fit(tr, tr[TARGET], groups=tr["SEASON"])
        out[name] = m.predict(te)
    return out


def summarize(preds, models):
    rows = []
    for name in models:
        rows.append({"modelo": name,
                     "MAE (vitórias/82)": mae_wins(preds[TARGET], preds[name]),
                     "Spearman conf.": spearman_conf(preds, name)})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- gráficos
BLUE, RED, GREY = "#1f6fb4", "#c0392b", "#999999"


def plot_pred_vs_real(preds, best, n, lang):
    t = L[lang]
    fig, axes = plt.subplots(1, 2, figsize=(14, 6.5), sharex=True, sharey=True)
    real = preds[TARGET] * 82
    for ax, col, title in [(axes[0], "Baseline: aproveitamento atual", t["baseline_keep"]),
                           (axes[1], best, f"{best} (LOSO)")]:
        p = preds[col] * 82
        ax.scatter(p, real, s=22, alpha=0.55, color=BLUE if col == best else GREY)
        ax.plot([0, 82], [0, 82], "k--", lw=1)
        ax.set_title(f"{title}\nMAE = {mae_wins(preds[TARGET], preds[col]):.2f} {t['wins']}")
        ax.set_xlabel(t["pred_wins"])
        ax.set_xlim(0, 82); ax.set_ylim(0, 82); ax.grid(alpha=0.3)
    axes[0].set_ylabel(t["real_wins"])
    fig.suptitle(t["pvr_title"].format(n=n), y=1.02)
    fig.savefig(fig_path("previsto_vs_real.png", lang)); plt.close(fig)


def plot_ridge_coefs(coef_tab, lang):
    t = L[lang]
    names = [t["feat"][f] for f in coef_tab.index]
    y = np.arange(len(names))
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.barh(y + 0.2, coef_tab["Linear (OLS)"], height=0.4, color=GREY, label=t["ols"])
    ax.barh(y - 0.2, coef_tab["Ridge"], height=0.4, color=BLUE, label="Ridge")
    ax.set_yticks(y); ax.set_yticklabels(names)
    ax.axvline(0, color="k", lw=0.8)
    ax.set_xlabel(t["coef_x"]); ax.set_title(t["coef_title"])
    ax.legend(loc="upper left"); ax.grid(axis="x", alpha=0.3)
    fig.savefig(fig_path("coeficientes_ridge.png", lang)); plt.close(fig)


def plot_shrinkage(df, n, lang):
    """Ilustra a regressão à média: final x aproveitamento após N jogos."""
    t = L[lang]
    x, y = df.win_pct, df[TARGET]
    b, a = np.polyfit(x, y, 1)
    fig, ax = plt.subplots(figsize=(8, 6.5))
    ax.scatter(x, y, s=20, alpha=0.5, color=BLUE)
    xs = np.linspace(0, 1, 50)
    ax.plot(xs, xs, "k--", lw=1, label=t["no_reg"])
    ax.plot(xs, a + b * xs, color=RED, lw=2.5, label=f"{t['fit']}: y = {a:.2f} + {b:.2f}x")
    ax.axhline(0.5, color="grey", lw=0.8)
    ax.set_xlabel(t["pct_n"].format(n=n)); ax.set_ylabel(t["pct_final"])
    ax.set_title(t["rtm_title"]); ax.legend(loc="upper left"); ax.grid(alpha=0.3)
    fig.savefig(fig_path("regressao_a_media.png", lang)); plt.close(fig)
    return a, b


def plot_corr(df, n, lang):
    t = L[lang]
    cols = FEATURES + [TARGET]
    names = [t["feat"].get(c, t["pct_final"]) for c in FEATURES] + [t["pct_final"]]
    C = df[cols].corr().to_numpy()
    fig, ax = plt.subplots(figsize=(9, 7.5))
    im = ax.imshow(C, cmap="RdBu_r", vmin=-1, vmax=1)
    for i in range(len(cols)):
        for j in range(len(cols)):
            ax.text(j, i, f"{C[i, j]:.2f}", ha="center", va="center", fontsize=11,
                    color="white" if abs(C[i, j]) > 0.7 else "black")
    ax.set_xticks(range(len(cols))); ax.set_xticklabels(names, rotation=40, ha="right")
    ax.set_yticks(range(len(cols))); ax.set_yticklabels(names)
    ax.set_title(t["corr_title"].format(n=n))
    fig.colorbar(im, ax=ax, shrink=0.8)
    fig.savefig(fig_path("correlacao_features.png", lang)); plt.close(fig)


# ---------------------------------------------------------------- main
PREFERENCE = ["Ridge", "Lasso", "Regressão Linear", "Random Forest"]


def choose_best(loso, table):
    """Entre os modelos treinados cujo MAE LOSO está a até 1 EP (entre temporadas)
    do menor MAE, escolhe o mais regularizado/estável segundo PREFERENCE."""
    learned = table[~table.modelo.str.startswith("Baseline")].copy()
    top = learned.iloc[0]["modelo"]
    per_season = loso.groupby("SEASON").apply(
        lambda g: mae_wins(g[TARGET], g[top]), include_groups=False)
    se = per_season.std(ddof=1) / np.sqrt(len(per_season))
    thr = learned["MAE (vitórias/82) LOSO"].min() + se
    cands = learned[learned["MAE (vitórias/82) LOSO"] <= thr]["modelo"].tolist()
    best = next(m for m in PREFERENCE if m in cands)
    print(f"\nEP do MAE entre temporadas = {se:.3f} vitórias; limiar = {thr:.3f}; "
          f"candidatos = {cands} -> escolhido: {best}")
    return best


def fit_final(name, hist):
    m = make_models()[name]().fit(hist, hist[TARGET], groups=hist["SEASON"])
    return m


def main():
    hist = pd.read_csv(PROCESSED / "features_hist.csv")
    cur = pd.read_csv(PROCESSED / "features_2026-27.csv")
    models = make_models()

    loso = loso_predictions(hist, models)
    hold = holdout_predictions(hist, models)
    t_loso = summarize(loso, models)
    t_hold = summarize(hold, models)
    table = t_loso.merge(t_hold, on="modelo", suffixes=(" LOSO", " holdout"))
    table = table.sort_values("MAE (vitórias/82) LOSO").reset_index(drop=True)
    table.round(3).to_csv(RESULTS / "comparacao_modelos.csv", index=False)
    loso.to_csv(RESULTS / "predicoes_loso.csv", index=False)

    best = choose_best(loso, table)
    (RESULTS / "melhor_modelo.txt").write_text(best, encoding="utf-8")

    pd.set_option("display.width", 200)
    print("=== Comparação de modelos ===")
    print(table.round(3).to_string(index=False))
    print(f"Melhor modelo: {best}")

    n = int(hist.gp.iloc[0])
    for lang in LANGS:
        plot_pred_vs_real(loso, best, n, lang)
        a, b = plot_shrinkage(hist, n, lang)
        plot_corr(hist, n, lang)

    # Ridge no histórico completo: coeficientes
    ridge = fit_final("Ridge", hist).best_estimator_
    alpha = ridge.named_steps["model"].alpha
    coefs = pd.Series(ridge.named_steps["model"].coef_, index=FEATURES)
    lr = LinearRegression().fit(StandardScaler().fit_transform(hist[FEATURES]), hist[TARGET])
    coef_tab = pd.DataFrame({"Ridge": coefs, "Linear (OLS)": lr.coef_}).round(4)
    coef_tab.to_csv(RESULTS / "coeficientes_ridge.csv")
    for lang in LANGS:
        plot_ridge_coefs(coef_tab, lang)
    print(f"\nRidge alpha (CV agrupada) = {alpha:.3g}; intercepto = {ridge.named_steps['model'].intercept_:.3f}")
    print(coef_tab.to_string())
    print(f"Regressão simples final ~ win_pct({n}j): final = {a:.3f} + {b:.3f} * win_pct")
    pd.Series({"intercepto": a, "inclinacao": b, "alpha_ridge": alpha}).to_csv(
        RESULTS / "encolhimento.csv", header=["valor"])

    # Previsão 2026-27 com o melhor modelo treinado em todo o histórico
    m = fit_final(best, hist)
    cur["pred_win_pct"] = m.predict(cur)
    cur["pred_wins_82"] = cur["pred_win_pct"] * 82
    cur["rank_conf"] = cur.groupby("CONF")["pred_win_pct"].rank(ascending=False, method="first").astype(int)
    out = cur.sort_values(["CONF", "rank_conf"])[
        ["CONF", "rank_conf", "TEAM", "wins", "gp", "win_pct", "pyth", "prev_win_pct",
         "pred_win_pct", "pred_wins_82"]]
    out.round(3).to_csv(RESULTS / "projecao_modelo_2026-27.csv", index=False)
    print(f"\nProjeção 2026-27 ({best}):")
    print(out.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
