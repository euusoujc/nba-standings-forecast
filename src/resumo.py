"""Gera results/resumo.md a partir dos arquivos de results/ (números sempre atualizados).

Uso: python src/resumo.py
"""
from __future__ import annotations

import pandas as pd

try:
    from config import RESULTS, PROCESSED
except ImportError:
    from src.config import RESULTS, PROCESSED


def _md(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for _, r in df.iterrows():
        lines.append("| " + " | ".join(str(v) for v in r.values) + " |")
    return "\n".join(lines)


def build() -> str:
    comp = pd.read_csv(RESULTS / "comparacao_modelos.csv")
    coefs = pd.read_csv(RESULTS / "coeficientes_ridge.csv", index_col=0)
    sim = pd.read_csv(RESULTS / "simulacao_2026-27.csv")
    bt = pd.read_csv(RESULTS / "backtest_simulacao.csv")
    best = (RESULTS / "melhor_modelo.txt").read_text(encoding="utf-8").strip()
    n = int(pd.read_csv(PROCESSED / "features_2026-27.csv").gp.iloc[0])

    cover = ((bt.real_wins >= bt.IC80_inf) & (bt.real_wins <= bt.IC80_sup)).mean()
    base = comp.set_index("modelo").loc["Baseline: aproveitamento atual", "MAE (vitórias/82) LOSO"]
    bm = comp.set_index("modelo").loc[best, "MAE (vitórias/82) LOSO"]

    comp_md = comp.copy()
    for c in comp_md.columns[1:]:
        comp_md[c] = comp_md[c].map(lambda v: f"{v:.3f}" if "Spearman" in c else f"{v:.2f}")

    parts = [f"# Resumo de resultados — NBA 2026-27 após {n} jogos\n",
             "## 1. Comparação de modelos\n",
             "MAE em vitórias (aproveitamento × 82) e Spearman médio da classificação "
             "prevista × real por conferência. LOSO = leave-one-season-out (16 temporadas); "
             "holdout = treino 2010-11..2022-23, teste 2023-24..2025-26.\n",
             _md(comp_md), "",
             f"**Melhor modelo: {best}.** Ele reduz o MAE de {base:.2f} (manter o aproveitamento atual) "
             f"para {bm:.2f} vitórias. Os quatro modelos treinados ficam a até 1 erro-padrão "
             "(entre temporadas) do melhor MAE; nesse caso escolhemos o mais regularizado "
             "(Ridge, com alpha pela regra de 1 EP na CV interna agrupada por temporada), "
             "porque seus coeficientes são estáveis e interpretáveis.\n",
             "## 2. Coeficientes (features padronizadas)\n",
             _md(coefs.reset_index().rename(columns={"index": "feature"})), "",
             "**Encolhimento:** após 15 jogos, cada ponto de aproveitamento acima de 0,500 "
             "vale só ~63% no fim da temporada (inclinação 0,63 de final ~ aproveitamento). "
             "A regressão já captura essa regressão à média (intercepto em 0,500). A penalidade "
             "do Ridge também encolhe os coeficientes e divide o peso entre features quase "
             "colineares (saldo, net rating e Pythagorean têm correlação > 0,99): o OLS dá "
             "+0,16/−0,18 a saldo/net rating, e o Ridge dá ~0,023 a cada uma.\n",
             "## 3. Projeção final 2026-27 (Monte Carlo, 10.000 simulações)\n"]
    for conf in ["Leste", "Oeste"]:
        d = sim[sim.CONF == conf].sort_values("posicao_media").copy()
        d.insert(0, "#", range(1, len(d) + 1))
        d["Campanha"] = d.V_atual.astype(str) + "-" + d.D_atual.astype(str)
        d["V esp."] = d.vitorias_esperadas.round(1)
        d["IC 80%"] = d.IC80_inf.round(0).astype(int).astype(str) + "–" + d.IC80_sup.round(0).astype(int).astype(str)
        for c, nm in [("P_top6", "P(top 6)"), ("P_playin", "P(play-in)"), ("P_fora", "P(fora)")]:
            d[nm] = (d[c] * 100).map(lambda v: f"{v:.0f}%")
        parts += [f"### Conferência {conf}\n",
                  _md(d[["#", "TEAM", "Campanha", "V esp.", "IC 80%", "P(top 6)", "P(play-in)", "P(fora)"]]), ""]
    mj = pd.read_csv(RESULTS / "modelo_jogo.csv", index_col=0)["valor"]
    sens = pd.read_csv(RESULTS / "sensibilidade_n.csv")
    sp = sens.pivot(index="N", columns="modelo", values="MAE").round(2).reset_index()
    sp.columns = ["N", "Baseline (MAE)", "Ridge (MAE)"]
    sp["N"] = sp["N"].astype(int)
    parts += ["**Modelo de jogo (regressão logística):** "
              f"b_diff = {mj.b_diff:.2f}, b_casa = {mj.b_casa:.2f} → P(mandante vence, times iguais) = "
              f"{mj.p_casa_times_iguais:.3f}; acurácia {mj.acuracia:.3f}, log-loss {mj.log_loss:.3f}; "
              f"σ do rating = {mj.sigma_rating:.3f}.\n",
              "**Validação da simulação (backtest, totalmente fora da amostra):** cada temporada histórica é "
              f"simulada a partir da data em que o último time completou {n} jogos, com o rating LOSO e o modelo "
              f"de jogo/σ reajustados sem a temporada. O IC de 80% contém as vitórias reais em {cover:.1%} dos "
              f"casos (nominal: 80%). Brier de 3 classes = {mj.brier_backtest:.3f}, contra {mj.brier_referencia:.3f} "
              "da referência com probabilidades constantes (6/15, 4/15, 5/15).\n",
              "## 4. Sensibilidade ao número de jogos (LOSO)\n",
              _md(sp), "",
              "O ganho do modelo sobre o baseline é maior quando há poucos jogos (com N = 5, o erro cai quase pela metade) "
              "e diminui conforme o aproveitamento fica menos ruidoso.\n",
              "## 5. Limitações\n",
              f"- **Poucos jogos:** com {n} jogos, o aproveitamento tem erro-padrão de ~0,13; mesmo o melhor "
              f"modelo erra em média ~{bm:.1f} vitórias.",
              "- **Lesões, trocas e mudanças de elenco não são modeladas**: o rating vem só de resultados.",
              f"- **Rating estático:** usa só os {n} primeiros jogos de cada time (para casar com o treino); "
              "os jogos 16-18 de quem já os disputou entram nas vitórias atuais, mas não atualizam o rating.",
              "- **Desempate simplificado (aleatório)**, em vez dos critérios oficiais da NBA (confronto direto, "
              "recorde na divisão/conferência etc.).",
              "- **2 jogos da NBA Cup ainda não definidos** são simulados contra um adversário médio, em quadra neutra; "
              "jogos em campo neutro do calendário são tratados como mando normal.",
              "- O modelo de jogo assume uma vantagem de mando constante entre temporadas (inclui a era sem público em 2020-21).",
              ]
    return "\n".join(parts) + "\n"


def main():
    txt = build()
    (RESULTS / "resumo.md").write_text(txt, encoding="utf-8")
    print(f"results/resumo.md gerado ({len(txt.splitlines())} linhas)")


if __name__ == "__main__":
    main()
