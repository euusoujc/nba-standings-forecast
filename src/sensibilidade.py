"""Análise complementar: como o erro de previsão cai com o número de jogos N.

Para cada N, reconstrói as features usando só os N primeiros jogos e avalia, por
leave-one-season-out, o baseline (mantém o aproveitamento) e o Ridge.

Uso: python src/sensibilidade.py
"""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

try:
    from config import RESULTS, HIST_SEASONS
    from coleta import load_all
    from features import build_features, current_n
    from modelos import make_models, loso_predictions, mae_wins, spearman_conf, TARGET
    from i18n import L, LANGS, fig_path
except ImportError:
    from src.config import RESULTS, HIST_SEASONS
    from src.coleta import load_all
    from src.features import build_features, current_n
    from src.modelos import make_models, loso_predictions, mae_wins, spearman_conf, TARGET
    from src.i18n import L, LANGS, fig_path

N_GRID = [5, 10, 15, 20, 25, 30, 41]
BASE = "Baseline: aproveitamento atual"


def run():
    games = load_all()
    n_now = current_n(games)
    grid = sorted(set(N_GRID + [n_now]))
    all_models = make_models()
    models = {k: all_models[k] for k in [BASE, "Ridge"]}
    rows = []
    for n in grid:
        hist = build_features(games, n)
        hist = hist[hist.SEASON.isin(HIST_SEASONS)].reset_index(drop=True)
        preds = loso_predictions(hist, models)
        for m in models:
            rows.append({"N": n, "modelo": m, "MAE": mae_wins(preds[TARGET], preds[m]),
                         "Spearman": spearman_conf(preds, m)})
        print(f"N={n:2d}  baseline MAE={rows[-2]['MAE']:.2f}  Ridge MAE={rows[-1]['MAE']:.2f}")
    res = pd.DataFrame(rows)
    res.round(3).to_csv(RESULTS / "sensibilidade_n.csv", index=False)
    return res, n_now


def plot(res, n_now, lang):
    t = L[lang]
    fig, ax = plt.subplots(figsize=(9, 6))
    for m, color, lab in [(BASE, "#999999", t["sens_base"]), ("Ridge", "#1f6fb4", t["sens_ridge"])]:
        d = res[res.modelo == m]
        ax.plot(d.N, d.MAE, "o-", color=color, lw=2.5, ms=7, label=lab)
    ax.axvline(n_now, color="#c0392b", ls="--", lw=1.5)
    lo, hi = ax.get_ylim()
    ax.text(n_now + 0.6, lo + 0.04 * (hi - lo), t["sens_now"].format(n=n_now), color="#c0392b",
            va="bottom")
    ax.set_xlabel(t["sens_x"]); ax.set_ylabel(t["sens_y"]); ax.set_title(t["sens_title"])
    ax.grid(alpha=0.3); ax.legend(loc="upper right")
    fig.savefig(fig_path("sensibilidade_n.png", lang)); plt.close(fig)


def main():
    res, n_now = run()
    for lang in LANGS:
        plot(res, n_now, lang)


if __name__ == "__main__":
    main()
