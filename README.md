# NBA 2026-27: previsão da classificação a partir dos primeiros jogos

Projeto final de Aprendizado de Máquina (UFABC, 2026.3).

**Autores:** [Nome do Autor 1] (RA [RA do Autor 1]) e Lucas Amorim de Souza (RA 11202321209).

Com uns 15 jogos disputados, o projeto prevê o aproveitamento final de cada time e a chance de ele terminar no
**top 6**, no **play-in (7-10)** ou **fora**, por conferência. A previsão é refeita com 0, 5, 10 e 15 jogos para
mostrar quanto cada bloco de partidas acrescenta.

## Um projeto vivo

Os dados vêm direto da API pública da NBA (`stats.nba.com`, via `nba_api`). Os números deste repositório são uma foto
de **22/11/2026** (N = 15 jogos), mas dá para atualizar a qualquer momento da temporada:

```powershell
python src/coleta.py --refresh-current
```

Depois, rode o notebook (ou os scripts abaixo) de novo. N passa a ser o número de jogos do dia, e todas as tabelas,
figuras e o `results/resumo.md` são regerados com os jogos mais recentes. Para acrescentar uma versão nova (por
exemplo, 20 jogos), inclua o número em `VERSIONS` no `src/versoes.py`. Os textos do artigo e dos slides citam os
números da foto de 22/11 e precisam ser revistos à mão se você atualizar.

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
python src/coleta.py         # baixa/usa o cache de data/raw (adicione --refresh-current para atualizar 2026-27)
python src/features.py       # data/processed/features_*.csv
python src/modelos.py        # results/comparacao_modelos.csv + figuras
python src/simulacao.py      # Monte Carlo + backtest fora da amostra + calibração + heatmap
python src/versoes.py        # versões com 0, 5, 10 e 15 jogos (~1 min)
python src/sensibilidade.py  # erro x número de jogos N (alguns minutos)
python src/resumo.py         # results/resumo.md
python artigo/gerar_tabelas.py  # tabelas e figuras do artigo
python apresentacao/build.py    # slides HTML
```

Todas as figuras são geradas em PT (`figures/`) e EN (`figures/en/`).

## Entregáveis

- **Código:** `notebooks/projeto.ipynb`.
- **Apresentação (lightning talk, 14 slides):** `apresentacao/apresentacao_pt.html` e `apresentacao/apresentacao_en.html`.
  São arquivos únicos: abra no navegador e navegue com as setas ou os pontos à direita. O roteiro de fala está em
  `apresentacao/roteiro_pt.md` (e `.txt`, e as versões `_en`). Para regenerar depois de mudar resultados ou textos,
  edite `slides_<lang>.body.html` e rode `python apresentacao/build.py`.
- **Artigo (IEEE):** `artigo/pt/main.tex` e `artigo/en/main.tex`. As tabelas (`tab_*.tex`) e as figuras saem de
  `results/` via `python artigo/gerar_tabelas.py`. Para compilar no Overleaf, compacte a pasta `artigo/pt` (ou
  `artigo/en`) e suba em *New Project → Upload Project*.

A primeira coleta leva ~10 min (17 temporadas, 1 requisição/s com retry). Depois disso, tudo
vem do cache em `data/raw/`. Seed fixa: 42.

## Estrutura

```
data/raw/          game logs por temporada (LeagueGameLog) e calendário 2026-27 (ScheduleLeagueV2)
data/processed/    games.csv, features_hist.csv, features_2026-27.csv, remaining_2026-27.csv
src/config.py      caminhos, temporadas, conferências, seed
src/coleta.py      Fase 1 – coleta com cache e retry
src/features.py    Fase 2 – features dos N primeiros jogos (sem vazamento)
src/modelos.py     Fase 3 – baselines, Linear/Ridge/Lasso/RF, LOSO + holdout temporal
src/simulacao.py   Fase 4 – modelo de jogo logístico + Monte Carlo (10.000×) + backtest
src/versoes.py     Fase 4b – pipeline refeito com 0, 5, 10 e 15 jogos
src/sensibilidade.py  análise complementar: MAE x N
src/i18n.py        rótulos PT/EN das figuras
src/resumo.py      Fase 5 – gera results/resumo.md
apresentacao/      slides HTML (PT e EN), roteiros e build.py
artigo/            artigo LaTeX IEEE (PT e EN) + gerar_tabelas.py
notebooks/         projeto.ipynb (pipeline completo com explicações)
figures/           PNGs finais (200 dpi)
results/           tabelas CSV e resumo.md
```

## Principais resultados

Veja [results/resumo.md](results/resumo.md). Em resumo:

- O Ridge reduz o erro de ~7,6 para ~5,6 vitórias em relação a manter o aproveitamento atual. No backtest histórico
  (fora da amostra), o intervalo de 80% da simulação cobre 81% dos resultados reais.
- Versões: o Brier do backtest cai de 0,533 (pré-temporada) para 0,488 (5 jogos), 0,444 (10) e 0,421 (15), e o erro
  nas vitórias finais cai de 7,8 para 5,3.
- Lesões, trocas e mudanças de elenco não são modeladas: o rating vem só dos resultados.

## Uso de IA, licença e créditos

- **Uso de IA.** Usamos o assistente Claude, da Anthropic, com o modelo **Claude Opus**, por meio do Claude Code, para
  implementar e depurar o código, revisar a metodologia e redigir e revisar o artigo, os slides e o roteiro (PT e EN).
  Os autores definiram a pergunta, os dados, os modelos e o protocolo de validação, conferiram os resultados e
  respondem pelo conteúdo. A declaração completa está no fim do artigo.
- **Dados.** As estatísticas são da NBA, obtidas em `stats.nba.com` pela biblioteca
  [nba_api](https://github.com/swar/nba_api) (licença MIT). Os dados pertencem à NBA e foram usados só para fins
  acadêmicos, sem uso comercial; os CSVs em `data/` estão aqui apenas para reprodutibilidade.
- **Código.** Ainda sem licença de software definida. Se os autores quiserem permitir reuso, basta adicionar um
  arquivo `LICENSE` (por exemplo, MIT).
- **Bibliotecas:** pandas, NumPy, scikit-learn, SciPy, Matplotlib e Jupyter.
