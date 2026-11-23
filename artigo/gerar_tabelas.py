"""Gera as tabelas LaTeX do artigo (EN e PT) a partir de results/ e copia as figuras.

Uso: python artigo/gerar_tabelas.py
Saída: artigo/en/tab_*.tex, artigo/pt/tab_*.tex, artigo/<lang>/figures/*.png e
       artigo/overleaf_<lang>.zip (pacote pronto para subir no Overleaf)
"""
import shutil
import zipfile
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RES = ROOT / "results"

MODEL_NAMES = {
    "en": {"Regressão Linear": "Linear regression (OLS)", "Ridge": "Ridge",
           "Lasso": "Lasso", "Random Forest": "Random forest",
           "Baseline: Pythagorean": "Baseline: Pythagorean",
           "Baseline: aproveitamento atual": "Baseline: keep current win \\%"},
    "pt": {"Regressão Linear": "Regressão linear (OLS)", "Ridge": "Ridge",
           "Lasso": "Lasso", "Random Forest": "Random forest",
           "Baseline: Pythagorean": "Baseline: Pythagorean",
           "Baseline: aproveitamento atual": "Baseline: mantém aproveitamento"},
}
FEAT = {
    "en": {"win_pct": "Win \\%", "pd_pg": "Point diff./game", "net_rtg": "Net rating",
           "pyth": "Pythagorean exp.", "sos": "Strength of schedule", "prev_win_pct": "Prev. season win \\%"},
    "pt": {"win_pct": "Aproveitamento", "pd_pg": "Saldo/jogo", "net_rtg": "Net rating",
           "pyth": "Pythagorean", "sos": "Força de tabela", "prev_win_pct": "Aprov. temp. anterior"},
}
FIGS = ["regressao_a_media.png", "correlacao_features.png", "previsto_vs_real.png",
        "sensibilidade_n.png", "calibracao_simulacao.png", "heatmap_posicoes.png",
        "coeficientes_ridge.png", "probabilidades_top6_playin.png",
        "versoes_trajetoria.png", "versoes_backtest.png"]


def num(x, d, lang):
    s = f"{x:.{d}f}"
    return s.replace(".", "{,}") if lang == "pt" else s


def tab_models(lang):
    df = pd.read_csv(RES / "comparacao_modelos.csv")
    best_mae = df.iloc[:, 1].min()
    rows = []
    for _, r in df.iterrows():
        name = MODEL_NAMES[lang][r.iloc[0]]
        if r.iloc[0] == "Ridge":
            name = f"\\textbf{{{name}}}"
        rows.append(f"{name} & {num(r.iloc[1], 2, lang)} & {num(r.iloc[2], 3, lang)} & "
                    f"{num(r.iloc[3], 2, lang)} & {num(r.iloc[4], 3, lang)} \\\\")
    return "\n".join(rows)


def tab_coefs(lang):
    df = pd.read_csv(RES / "coeficientes_ridge.csv", index_col=0)
    return "\n".join(f"{FEAT[lang][f]} & {num(r['Linear (OLS)'], 3, lang)} & {num(r['Ridge'], 3, lang)} \\\\"
                     for f, r in df.iterrows())


def tab_sens(lang):
    df = pd.read_csv(RES / "sensibilidade_n.csv")
    p = df.pivot(index="N", columns="modelo", values="MAE")
    s = df.pivot(index="N", columns="modelo", values="Spearman")
    b = "Baseline: aproveitamento atual"
    rows = []
    for n in p.index:
        gain = 100 * (1 - p.loc[n, "Ridge"] / p.loc[n, b])
        rows.append(f"{n} & {num(p.loc[n, b], 2, lang)} & {num(p.loc[n, 'Ridge'], 2, lang)} & "
                    f"{num(gain, 0, lang)}\\% & {num(s.loc[n, 'Ridge'], 3, lang)} \\\\")
    return "\n".join(rows)


def tab_proj(lang):
    sim = pd.read_csv(RES / "simulacao_2026-27.csv")
    halves = []
    for conf in ["Leste", "Oeste"]:
        d = sim[sim.CONF == conf].sort_values("posicao_media").reset_index(drop=True)
        halves.append([
            f"{i + 1} & {r.TEAM} & {r.V_atual}--{r.D_atual} & {num(r.vitorias_esperadas, 1, lang)} & "
            f"{int(round(r.IC80_inf))}--{int(round(r.IC80_sup))} & "
            f"{num(100 * r.P_top6, 0, lang)} & {num(100 * r.P_playin, 0, lang)} & {num(100 * r.P_fora, 0, lang)}"
            for i, r in d.iterrows()])
    return "\n".join(f"{a} & {b} \\\\" for a, b in zip(*halves))


def tab_versions(lang):
    df = pd.read_csv(RES / "versoes_resumo.csv")
    rows = []
    for _, r in df.iterrows():
        cut = pd.Timestamp(r.data_corte)
        date = cut.strftime("%d/%m") if lang == "pt" else cut.strftime("%b %d").replace(" 0", " ")
        rows.append(f"{r.versao} & {date} & {r.jogos_no_corte.replace('-', '--')} & "
                    f"{num(r.MAE_LOSO_baseline, 2, lang)} & {num(r.MAE_LOSO_ridge, 2, lang)} & "
                    f"{num(r.sigma, 3, lang)} & {num(r.brier_backtest, 3, lang)} & "
                    f"{num(100 * r.cobertura_ic80, 1, lang)}\\% & {num(r.MAE_backtest_vitorias, 2, lang)} \\\\")
    return "\n".join(rows)


def main():
    for lang in ["en", "pt"]:
        out = HERE / lang
        (out / "figures").mkdir(parents=True, exist_ok=True)
        for name, fn in [("models", tab_models), ("coefs", tab_coefs), ("sens", tab_sens), ("proj", tab_proj),
                         ("versions", tab_versions)]:
            (out / f"tab_{name}.tex").write_text(fn(lang) + "\n", encoding="utf-8")
        src = ROOT / "figures" / ("en" if lang == "en" else "")
        for f in FIGS:
            shutil.copy(src / f, out / "figures" / f)
        print(f"{lang}: tabelas e {len(FIGS)} figuras prontas em {out}")
        make_zip(lang)


def make_zip(lang):
    """Pacote para o Overleaf (New Project > Upload Project): main.tex, tabelas e figuras."""
    out = HERE / lang
    zpath = HERE / f"overleaf_{lang}.zip"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(out / "main.tex", "main.tex")
        for t in sorted(out.glob("tab_*.tex")):
            z.write(t, t.name)
        for f in FIGS:
            z.write(out / "figures" / f, f"figures/{f}")
    print(f"{lang}: {zpath.name} atualizado")


if __name__ == "__main__":
    main()
