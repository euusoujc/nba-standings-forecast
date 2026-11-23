"""Rótulos das figuras em português (pt) e inglês (en).

Figuras em PT vão para figures/, em EN para figures/en/.
"""
try:
    from config import FIGURES
except ImportError:
    from src.config import FIGURES

LANGS = ["pt", "en"]
(FIGURES / "en").mkdir(parents=True, exist_ok=True)


def fig_path(name: str, lang: str):
    return (FIGURES / name) if lang == "pt" else (FIGURES / "en" / name)


L = {
    "pt": {
        "pred_wins": "Vitórias previstas (escala 82 jogos)",
        "real_wins": "Vitórias reais (escala 82 jogos)",
        "baseline_keep": "Baseline: mantém aproveitamento",
        "wins": "vitórias",
        "pvr_title": "Previsto x real após {n} jogos — 16 temporadas (2010-11 a 2025-26)",
        "coef_x": "Coeficiente (features padronizadas)",
        "coef_title": "Ridge x OLS: coeficientes padronizados",
        "ols": "Regressão linear (OLS)",
        "no_reg": "sem regressão (y = x)",
        "fit": "ajuste",
        "pct_n": "Aproveitamento após {n} jogos",
        "pct_final": "Aproveitamento final",
        "rtm_title": "Regressão à média",
        "corr_title": "Correlação entre as features (após {n} jogos)",
        "sens_x": "Jogos disputados (N)",
        "sens_y": "MAE (vitórias, escala 82)",
        "sens_title": "Erro de previsão x número de jogos (LOSO)",
        "sens_base": "Baseline: mantém aproveitamento",
        "sens_ridge": "Ridge",
        "sens_now": "hoje (N = {n})",
        "position": "Posição final na conferência",
        "conf": "Conferência {c}",
        "prob_pct": "Probabilidade (%)",
        "heat_title": "NBA 2026-27: probabilidade de cada posição ({sims} simulações)",
        "top6": "Top 6", "playin": "Play-in (7-10)", "out": "Fora",
        "probs_title": "Probabilidade de top 6 / play-in / fora (vitórias esperadas entre parênteses)",
        "W": "V",
        "calib_x": "Probabilidade prevista",
        "calib_y": "Frequência observada",
        "calib_title": "Calibração da simulação (backtest, 16 temporadas)",
        "perfect": "calibração perfeita",
        "Leste": "Leste", "Oeste": "Oeste",
        "feat": {"win_pct": "aproveitamento", "pd_pg": "saldo/jogo", "net_rtg": "net rating",
                 "pyth": "Pythagorean", "sos": "força de tabela", "prev_win_pct": "temp. anterior"},
    },
    "en": {
        "pred_wins": "Predicted wins (82-game scale)",
        "real_wins": "Actual wins (82-game scale)",
        "baseline_keep": "Baseline: keep current win %",
        "wins": "wins",
        "pvr_title": "Predicted vs actual after {n} games — 16 seasons (2010-11 to 2025-26)",
        "coef_x": "Coefficient (standardized features)",
        "coef_title": "Ridge vs OLS: standardized coefficients",
        "ols": "Linear regression (OLS)",
        "no_reg": "no regression (y = x)",
        "fit": "fit",
        "pct_n": "Win % after {n} games",
        "pct_final": "Final win %",
        "rtm_title": "Regression to the mean",
        "corr_title": "Feature correlation (after {n} games)",
        "sens_x": "Games played (N)",
        "sens_y": "MAE (wins, 82-game scale)",
        "sens_title": "Prediction error vs number of games (LOSO)",
        "sens_base": "Baseline: keep current win %",
        "sens_ridge": "Ridge",
        "sens_now": "today (N = {n})",
        "position": "Final conference position",
        "conf": "{c} Conference",
        "prob_pct": "Probability (%)",
        "heat_title": "NBA 2026-27: probability of each position ({sims} simulations)",
        "top6": "Top 6", "playin": "Play-in (7-10)", "out": "Out",
        "probs_title": "Probability of top 6 / play-in / out (expected wins in parentheses)",
        "W": "W",
        "calib_x": "Predicted probability",
        "calib_y": "Observed frequency",
        "calib_title": "Simulation calibration (backtest, 16 seasons)",
        "perfect": "perfect calibration",
        "Leste": "Eastern", "Oeste": "Western",
        "feat": {"win_pct": "win %", "pd_pg": "point diff/game", "net_rtg": "net rating",
                 "pyth": "Pythagorean", "sos": "strength of schedule", "prev_win_pct": "prev. season"},
    },
}
