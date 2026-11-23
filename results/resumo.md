# Resumo de resultados — NBA 2026-27 após 15 jogos

## 1. Comparação de modelos

MAE em vitórias (aproveitamento × 82) e Spearman médio da classificação prevista × real por conferência. LOSO = leave-one-season-out (16 temporadas); holdout = treino 2010-11..2022-23, teste 2023-24..2025-26.

| modelo | MAE (vitórias/82) LOSO | Spearman conf. LOSO | MAE (vitórias/82) holdout | Spearman conf. holdout |
|---|---|---|---|---|
| Regressão Linear | 5.50 | 0.785 | 5.22 | 0.867 |
| Ridge | 5.62 | 0.784 | 5.35 | 0.864 |
| Lasso | 5.68 | 0.788 | 5.45 | 0.877 |
| Random Forest | 5.72 | 0.779 | 5.42 | 0.816 |
| Baseline: Pythagorean | 6.83 | 0.749 | 6.13 | 0.819 |
| Baseline: aproveitamento atual | 7.60 | 0.743 | 6.93 | 0.817 |

**Melhor modelo: Ridge.** Ele reduz o MAE de 7.60 (manter o aproveitamento atual) para 5.62 vitórias. Os quatro modelos treinados ficam a até 1 erro-padrão (entre temporadas) do melhor MAE; nesse caso escolhemos o mais regularizado (Ridge, com alpha pela regra de 1 EP na CV interna agrupada por temporada), porque seus coeficientes são estáveis e interpretáveis.

## 2. Coeficientes (features padronizadas)

| feature | Ridge | Linear (OLS) |
|---|---|---|
| win_pct | 0.0356 | 0.0531 |
| pd_pg | 0.0231 | 0.1608 |
| net_rtg | 0.0225 | -0.1796 |
| pyth | 0.0236 | 0.0751 |
| sos | 0.0065 | 0.007 |
| prev_win_pct | 0.028 | 0.0315 |

**Encolhimento:** após 15 jogos, cada ponto de aproveitamento acima de 0,500 vale só ~63% no fim da temporada (inclinação 0.63 de final ~ aproveitamento). A regressão já captura essa regressão à média (intercepto perto de 0,500). A penalidade do Ridge também encolhe os coeficientes e divide o peso entre features quase colineares (saldo, net rating e Pythagorean têm correlação > 0,99): o OLS dá +0.16/-0.18 a saldo/net rating, e o Ridge dá 0.023/0.022.

## 3. Projeção final 2026-27 (Monte Carlo, 10.000 simulações)

### Conferência Leste

| # | TEAM | Campanha | V esp. | IC 80% | P(top 6) | P(play-in) | P(fora) |
|---|---|---|---|---|---|---|---|
| 1 | BOS | 11-6 | 55.8 | 48–63 | 97% | 3% | 0% |
| 2 | DET | 10-6 | 53.6 | 46–61 | 94% | 6% | 0% |
| 3 | PHI | 14-3 | 52.4 | 44–60 | 90% | 9% | 0% |
| 4 | NYK | 11-6 | 50.9 | 43–59 | 86% | 13% | 0% |
| 5 | ATL | 11-6 | 46.5 | 38–55 | 67% | 32% | 1% |
| 6 | CLE | 9-8 | 45.7 | 37–54 | 62% | 36% | 2% |
| 7 | MIA | 10-6 | 45.6 | 37–54 | 61% | 37% | 2% |
| 8 | TOR | 6-10 | 38.1 | 30–47 | 19% | 65% | 16% |
| 9 | ORL | 7-9 | 38.0 | 29–47 | 18% | 65% | 16% |
| 10 | IND | 5-12 | 30.7 | 23–39 | 3% | 41% | 56% |
| 11 | CHI | 4-12 | 28.2 | 20–36 | 1% | 28% | 71% |
| 12 | CHA | 4-11 | 27.8 | 20–36 | 1% | 26% | 73% |
| 13 | WAS | 7-11 | 27.7 | 20–35 | 0% | 24% | 76% |
| 14 | BKN | 3-12 | 24.0 | 17–32 | 0% | 11% | 89% |
| 15 | MIL | 1-16 | 20.2 | 13–28 | 0% | 3% | 97% |

### Conferência Oeste

| # | TEAM | Campanha | V esp. | IC 80% | P(top 6) | P(play-in) | P(fora) |
|---|---|---|---|---|---|---|---|
| 1 | SAS | 14-3 | 58.9 | 51–66 | 95% | 5% | 0% |
| 2 | LAL | 14-3 | 55.8 | 48–63 | 86% | 14% | 0% |
| 3 | HOU | 12-5 | 54.5 | 47–62 | 82% | 17% | 1% |
| 4 | MIN | 12-5 | 54.3 | 46–62 | 81% | 18% | 1% |
| 5 | OKC | 10-7 | 50.5 | 43–58 | 61% | 36% | 3% |
| 6 | POR | 10-6 | 50.2 | 42–58 | 59% | 38% | 3% |
| 7 | MEM | 12-5 | 48.5 | 40–57 | 48% | 46% | 6% |
| 8 | DEN | 10-5 | 48.5 | 40–57 | 47% | 47% | 6% |
| 9 | GSW | 9-8 | 43.2 | 35–51 | 19% | 60% | 21% |
| 10 | PHX | 8-7 | 41.8 | 33–50 | 14% | 57% | 29% |
| 11 | DAL | 10-7 | 39.7 | 32–48 | 8% | 51% | 42% |
| 12 | LAC | 4-11 | 29.5 | 21–38 | 0% | 8% | 92% |
| 13 | NOP | 5-13 | 26.6 | 19–34 | 0% | 3% | 97% |
| 14 | UTA | 3-15 | 23.2 | 16–31 | 0% | 1% | 99% |
| 15 | SAC | 2-14 | 19.7 | 13–27 | 0% | 0% | 100% |

**Modelo de jogo (regressão logística):** b_diff = 4.35, b_casa = 0.32 → P(mandante vence, times iguais) = 0.579; acurácia 0.643, log-loss 0.629; σ do rating = 0.085.

**Validação da simulação (backtest, totalmente fora da amostra):** cada temporada histórica é simulada a partir da data em que o último time completou 15 jogos, com o rating LOSO e o modelo de jogo/σ reajustados sem a temporada. O IC de 80% contém as vitórias reais em 81.0% dos casos (nominal: 80%). Brier de 3 classes = 0.421, contra 0.658 da referência com probabilidades constantes (6/15, 4/15, 5/15).

## 4. Sensibilidade ao número de jogos (LOSO)

| N | Baseline (MAE) | Ridge (MAE) |
|---|---|---|
| 5 | 13.3 | 7.18 |
| 10 | 9.09 | 6.25 |
| 15 | 7.6 | 5.62 |
| 20 | 6.64 | 5.34 |
| 25 | 6.15 | 4.94 |
| 30 | 5.31 | 4.61 |
| 41 | 3.94 | 3.6 |

O ganho do modelo sobre o baseline é maior quando há poucos jogos (com N = 5, o erro cai quase pela metade) e diminui conforme o aproveitamento fica menos ruidoso.

## 5. Versões com 0, 5, 10 e 15 jogos

Cada versão refaz o pipeline inteiro (features, Ridge, modelo de jogo, σ, backtest e Monte Carlo) na data em que o último time completou N jogos. V0 é a pré-temporada (só a temporada anterior).

| Versão | Data de corte | Jogos no corte | MAE LOSO baseline | MAE LOSO Ridge | σ | Brier backtest | Cobertura IC80 | MAE backtest (vitórias) |
|---|---|---|---|---|---|---|---|---|
| V0 | 2026-10-19 | 0-0 | 8.54 | 8.15 | 0.111 | 0.533 | 87.3% | 7.84 |
| V5 | 2026-11-02 | 5-8 | 13.30 | 7.18 | 0.101 | 0.488 | 80.6% | 6.95 |
| V10 | 2026-11-11 | 10-13 | 9.09 | 6.25 | 0.092 | 0.444 | 79.4% | 5.97 |
| V15 | 2026-11-22 | 15-18 | 7.60 | 5.62 | 0.085 | 0.421 | 81.0% | 5.32 |

| Conf. | Time | V0 (V esp.) | V5 (V esp.) | V10 (V esp.) | V15 (V esp.) | P(top 6) V0→V15 |
|---|---|---|---|---|---|---|
| Leste | BOS | 49.0 | 53.1 | 57.0 | 55.8 | 66% → 97% |
| Leste | DET | 50.8 | 54.6 | 55.1 | 53.6 | 72% → 94% |
| Leste | PHI | 43.1 | 48.8 | 50.1 | 52.4 | 45% → 90% |
| Leste | NYK | 46.9 | 43.6 | 49.9 | 50.9 | 59% → 86% |
| Leste | ATL | 43.6 | 45.4 | 46.2 | 46.5 | 47% → 67% |
| Leste | CLE | 46.7 | 45.9 | 46.3 | 45.7 | 58% → 62% |
| Leste | MIA | 42.1 | 35.3 | 37.2 | 45.6 | 42% → 61% |
| Leste | TOR | 43.4 | 48.8 | 43.2 | 38.1 | 46% → 19% |
| Leste | ORL | 43.1 | 36.3 | 34.1 | 38.0 | 46% → 18% |
| Leste | IND | 30.2 | 32.2 | 30.7 | 30.7 | 10% → 3% |
| Leste | CHI | 35.9 | 27.0 | 23.1 | 28.2 | 23% → 1% |
| Leste | CHA | 42.6 | 37.3 | 29.2 | 27.8 | 44% → 1% |
| Leste | WAS | 29.0 | 33.3 | 30.9 | 27.7 | 8% → 0% |
| Leste | BKN | 30.3 | 25.2 | 26.3 | 24.0 | 11% → 0% |
| Leste | MIL | 36.5 | 29.6 | 23.8 | 20.2 | 23% → 0% |
| Oeste | SAS | 51.7 | 51.8 | 57.0 | 58.9 | 74% → 95% |
| Oeste | LAL | 46.9 | 52.0 | 54.1 | 55.8 | 58% → 86% |
| Oeste | HOU | 46.6 | 56.4 | 54.1 | 54.5 | 57% → 82% |
| Oeste | MIN | 44.6 | 50.0 | 52.7 | 54.3 | 50% → 81% |
| Oeste | OKC | 52.8 | 52.7 | 55.5 | 50.5 | 78% → 61% |
| Oeste | POR | 41.2 | 50.1 | 50.1 | 50.2 | 39% → 59% |
| Oeste | DEN | 47.2 | 44.0 | 46.0 | 48.5 | 60% → 47% |
| Oeste | MEM | 32.7 | 46.7 | 44.3 | 48.5 | 14% → 48% |
| Oeste | GSW | 39.1 | 39.8 | 47.3 | 43.2 | 31% → 19% |
| Oeste | PHX | 43.2 | 33.9 | 36.5 | 41.8 | 45% → 14% |
| Oeste | DAL | 33.4 | 39.0 | 42.9 | 39.7 | 16% → 8% |
| Oeste | LAC | 41.5 | 34.0 | 31.1 | 29.5 | 39% → 0% |
| Oeste | NOP | 33.4 | 32.2 | 33.1 | 26.6 | 16% → 0% |
| Oeste | UTA | 31.2 | 27.7 | 21.7 | 23.2 | 11% → 0% |
| Oeste | SAC | 31.1 | 23.2 | 21.0 | 19.7 | 11% → 0% |

## 6. Limitações

- **Poucos jogos:** com 15 jogos, o aproveitamento tem erro-padrão de ~0,13; mesmo o melhor modelo erra em média ~5.6 vitórias.
- **Lesões, trocas e mudanças de elenco não são modeladas**: o rating vem só de resultados.
- **Rating estático:** usa só os 15 primeiros jogos de cada time (para casar com o treino); os jogos 16-18 de quem já os disputou entram nas vitórias atuais, mas não atualizam o rating.
- **Desempate simplificado (aleatório)**, em vez dos critérios oficiais da NBA (confronto direto, recorde na divisão/conferência etc.).
- **2 jogos da NBA Cup ainda não definidos** são simulados contra um adversário médio, em quadra neutra; jogos em campo neutro do calendário são tratados como mando normal.
- O modelo de jogo assume uma vantagem de mando constante entre temporadas (inclui a era sem público em 2020-21).
