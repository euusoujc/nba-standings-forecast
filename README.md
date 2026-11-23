# NBA 2026-27: previsão da classificação a partir dos primeiros jogos

Projeto final de Aprendizado de Máquina (UFABC). Com ~15-18 jogos disputados, o projeto prevê o aproveitamento final de
cada time e a probabilidade de ele terminar no **top 6**, no **play-in (7-10)** ou **fora**, por conferência.

## Como reproduzir

Requer Python 3.10+ (testado com 3.14 no Windows).

```powershell
pip install -r requirements.txt
```

Opção 1 — notebook (entrega de código), roda o pipeline inteiro:

```powershell
jupyter nbconvert --to notebook --execute --inplace notebooks/projeto.ipynb
```

Opção 2 — scripts, na ordem:

```powershell
python src/coleta.py      # baixa/usa o cache de data/raw (adicione --refresh-current para atualizar 2026-27)
python src/features.py    # data/processed/features_*.csv
python src/modelos.py     # results/comparacao_modelos.csv + figuras
python src/simulacao.py   # Monte Carlo + backtest fora da amostra + calibração + heatmap
python src/sensibilidade.py  # erro x número de jogos N (alguns minutos)
python src/resumo.py      # results/resumo.md
```

Todas as figuras são geradas em PT (`figures/`) e EN (`figures/en/`).

## Entregáveis

- **Código:** `notebooks/projeto.ipynb`.
- **Apresentação (lightning talk, 13 slides):** `apresentacao/apresentacao_en.html` e `apresentacao/apresentacao_pt.html`.
  São arquivos únicos: abra no navegador e navegue com as setas ou os pontos à direita. Para regenerar depois de
  mudar resultados ou textos, edite `slides_<lang>.body.html` e rode `python apresentacao/build.py`.
- **Artigo (IEEE):** `artigo/en/main.tex` e `artigo/pt/main.tex`. As tabelas (`tab_*.tex`) e as figuras saem de
  `results/` via `python artigo/gerar_tabelas.py`. Para compilar no Overleaf, suba `artigo/overleaf_en.zip`
  (ou `_pt.zip`) em *New Project → Upload Project*.

A primeira coleta leva ~10 min (17 temporadas, 1 requisição/s com retry). Depois disso, tudo vem do cache em `data/raw/`.
Os dados de 2026-27 congelados neste repositório vão até 22/11/2026 (N = 15 jogos). Seed fixa: 42.

## Estrutura

```
data/raw/          game logs por temporada (LeagueGameLog) e calendário 2026-27 (ScheduleLeagueV2)
data/processed/    games.csv, features_hist.csv, features_2026-27.csv, remaining_2026-27.csv
src/config.py      caminhos, temporadas, conferências, seed
src/coleta.py      Fase 1 – coleta com cache e retry
src/features.py    Fase 2 – features dos N primeiros jogos (sem vazamento)
src/modelos.py     Fase 3 – baselines, Linear/Ridge/Lasso/RF, LOSO + holdout temporal
src/simulacao.py   Fase 4 – modelo de jogo logístico + Monte Carlo (10.000×) + backtest
src/sensibilidade.py  análise complementar: MAE x N
src/i18n.py        rótulos PT/EN das figuras
src/resumo.py      Fase 5 – gera results/resumo.md
apresentacao/      slides HTML (PT e EN) + build.py
artigo/            artigo LaTeX IEEE (PT e EN) + gerar_tabelas.py
notebooks/         projeto.ipynb (pipeline completo com explicações)
figures/           PNGs finais (200 dpi)
results/           tabelas CSV e resumo.md
```

## Principais resultados

Veja [results/resumo.md](results/resumo.md). Resumo: o Ridge reduz o erro de ~7,6 para ~5,6 vitórias em relação a
manter o aproveitamento atual. No backtest histórico (fora da amostra), o intervalo de 80% da simulação cobre 81% dos
resultados reais.
