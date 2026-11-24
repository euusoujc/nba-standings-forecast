"""Cenas do vídeo explicativo (PT e EN).

Cada cena tem um visual (`kind` + campos) e a narração (`say`). Campos de texto
bilíngues usam L(pt, en). O gerar_video.py resolve tudo para um idioma.
"""


def L(pt, en):
    return {"pt": pt, "en": en}


SCENES = [
    # ------------------------------------------------------------------ abertura
    dict(kind="slide", n=1, say=L(
        "Olá! Neste vídeo vamos mostrar, passo a passo, o projeto final de Aprendizado de Máquina da UFABC: "
        "quinze jogos não são uma temporada. A ideia é prever como a temporada regular da NBA vai terminar "
        "quando ela mal começou. Vamos passar por quatro partes: o tema, as bases de dados e as fontes, "
        "a metodologia e, por fim, os resultados e as análises, mostrando o que foi construído em cada etapa.",
        "Hi! In this video we will walk you through our final Machine Learning project at UFABC: "
        "fifteen games are not a season. The idea is to predict how the NBA regular season will end "
        "when it has barely started. We will go through four parts: the topic, the data and its sources, "
        "the methodology and, finally, the results and the analysis, showing what we built at each step.")),

    # ------------------------------------------------------------------ 1. tema
    dict(kind="section", num="01", title=L("Tema", "Topic"),
         sub=L("A pergunta e o que o projeto entrega", "The question and what the project delivers"),
         say=L("Primeira parte: o tema.", "Part one: the topic.")),

    dict(kind="slide", n=2, say=L(
        "Tudo começa com uma pergunta simples. O Philadelphia está catorze a três. Isso é um time bom ou é sorte? "
        "A temporada regular da NBA tem oitenta e dois jogos por time. Com uns quinze jogos, cada time disputou "
        "menos de vinte por cento da temporada, e a classificação de novembro ainda engana muito. "
        "O projeto quer responder, para cada time, quantas vitórias ele deve ter no fim e qual a chance de terminar "
        "no top seis da conferência, que dá vaga direta nos playoffs, no play-in, do sétimo ao décimo lugar, "
        "ou fora, do décimo primeiro ao décimo quinto.",
        "It all starts with a simple question. Philadelphia is fourteen and three. Is that a good team, or just luck? "
        "The NBA regular season has eighty-two games per team. After about fifteen games, each team has played "
        "less than twenty percent of the season, and the November standings are still very misleading. "
        "For each team, the project answers how many wins it should end up with, and how likely it is to finish "
        "in its conference's top six, which means a direct playoff spot, in the play-in, seventh to tenth place, "
        "or out, eleventh to fifteenth.")),

    dict(kind="cards", eyebrow=L("O QUE O PROJETO ENTREGA", "WHAT THE PROJECT DELIVERS"),
         title=L("Uma previsão completa, por conferência", "A full forecast, by conference"),
         cards=[
             (L("VITÓRIAS", "WINS"), L("Vitórias esperadas", "Expected wins"),
              L("Média de 10.000 simulações, com intervalo de 80%.", "Mean of 10,000 simulations, with an 80% interval.")),
             (L("CHANCES", "ODDS"), L("Top 6 · play-in · fora", "Top 6 · play-in · out"),
              L("Probabilidade de cada desfecho para os 30 times.", "Probability of each outcome for all 30 teams.")),
             (L("VERSÕES", "VERSIONS"), L("V0 · V5 · V10 · V15", "V0 · V5 · V10 · V15"),
              L("A previsão refeita com 0, 5, 10 e 15 jogos.", "The forecast redone with 0, 5, 10 and 15 games.")),
             (L("PROJETO VIVO", "LIVE PROJECT"), L("Dados da API da NBA", "NBA API data"),
              L("Um comando atualiza tudo com os jogos mais recentes.", "One command refreshes everything with the latest games.")),
         ],
         say=L(
             "No fim, o projeto entrega quatro coisas. As vitórias esperadas de cada time, com um intervalo de oitenta por cento. "
             "As probabilidades de top seis, play-in e fora, para os trinta times. Quatro versões da previsão, feitas antes "
             "da estreia e depois de cinco, dez e quinze jogos, para mostrar quanto cada bloco de partidas acrescenta. "
             "E é um projeto vivo: como os dados vêm direto da API da NBA, basta rodar o pipeline de novo para atualizar "
             "a previsão em qualquer momento da temporada. Os números deste vídeo são uma foto de vinte e dois de novembro de 2026.",
             "In the end, the project delivers four things. Each team's expected wins, with an eighty percent interval. "
             "The probabilities of top six, play-in and out, for all thirty teams. Four versions of the forecast, made before "
             "opening night and after five, ten and fifteen games, to show how much each block of games adds. "
             "And it is a live project: since the data comes straight from the NBA API, you just rerun the pipeline to update "
             "the forecast at any point in the season. The numbers in this video are a snapshot from November twenty-second, 2026.")),

    # ------------------------------------------------------------------ 2. dados
    dict(kind="section", num="02", title=L("Bases e fontes", "Data and sources"),
         sub=L("De onde vêm os dados e como viram features", "Where the data comes from and how it becomes features"),
         say=L("Segunda parte: as bases de dados e as fontes.", "Part two: the data and its sources.")),

    dict(kind="cards", eyebrow=L("FONTE", "SOURCE"),
         title=L("API pública da NBA, via nba_api", "The public NBA API, through nba_api"),
         cards=[
             (L("FONTE", "SOURCE"), L("stats.nba.com", "stats.nba.com"),
              L("Biblioteca Python nba_api (licença MIT). Uso acadêmico.", "nba_api Python library (MIT license). Academic use.")),
             (L("ENDPOINT", "ENDPOINT"), L("LeagueGameLog", "LeagueGameLog"),
              L("Uma linha por time por jogo, de 2009-10 a 2026-27.", "One row per team per game, 2009-10 to 2026-27.")),
             (L("ENDPOINT", "ENDPOINT"), L("ScheduleLeagueV2", "ScheduleLeagueV2"),
              L("Calendário 2026-27: os 952 jogos que faltam.", "2026-27 schedule: the 952 games left.")),
             (L("CACHE", "CACHE"), L("data/raw/", "data/raw/"),
              L("1 requisição por segundo, com retry. Depois, tudo vem do cache.", "1 request per second, with retry. After that, everything comes from the cache.")),
         ],
         say=L(
             "Todos os dados vêm da API pública de estatísticas da NBA, o site stats ponto nba ponto com, acessada pela biblioteca "
             "Python nba underline api. Usamos dois endpoints. O League Game Log traz o registro de cada jogo da temporada regular, "
             "uma linha por time por jogo, com data, adversário, mando, resultado, pontos e estatísticas de arremesso. "
             "Baixamos dezessete temporadas, de 2009 a 2027. E o Schedule League V2 traz o calendário da temporada atual, "
             "de onde saem os novecentos e cinquenta e dois jogos que ainda faltam. Cada arquivo fica salvo em cache na pasta "
             "data barra raw. A primeira coleta leva uns dez minutos, a uma requisição por segundo; depois disso, tudo é local.",
             "All the data comes from the NBA's public stats API, the stats dot nba dot com site, accessed with the nba underscore api "
             "Python library. We use two endpoints. League Game Log gives the log of every regular season game, "
             "one row per team per game, with the date, opponent, home or away, result, points and shooting stats. "
             "We downloaded seventeen seasons, from 2009 to 2027. And Schedule League V2 gives the current season's schedule, "
             "which is where the nine hundred fifty-two remaining games come from. Every file is cached in the data slash raw folder. "
             "The first download takes about ten minutes, at one request per second; after that, everything is local.")),

    dict(kind="code", file="src/coleta.py", start=51,
         code='''def fetch_season(season: str, refresh: bool = False) -> pd.DataFrame:
    """Baixa (ou lê do cache) o game log de times da temporada regular."""
    path = RAW / f"gamelog_{season}.csv"
    if path.exists() and not refresh:
        return pd.read_csv(path, dtype={"GAME_ID": str})

    from nba_api.stats.endpoints import leaguegamelog

    def _call():
        return leaguegamelog.LeagueGameLog(
            season=season, player_or_team_abbreviation="T",
            season_type_all_star="Regular Season", timeout=TIMEOUT,
        ).get_data_frames()[0]

    df = _with_retry(_call, season)   # espera exponencial se falhar
    df.to_csv(path, index=False)
    return df''',
         eyebrow=L("FASE 1 · COLETA", "PHASE 1 · COLLECTION"),
         title=L("Coleta com cache e retry", "Collection with cache and retry"),
         notes=[L("Lê do cache se o arquivo já existe", "Reads from cache if the file exists"),
                L("--refresh-current baixa 2026-27 de novo", "--refresh-current re-downloads 2026-27"),
                L("Retry com espera exponencial", "Retry with exponential backoff")],
         say=L(
             "Este é o coração da coleta, no arquivo coleta ponto py. Se o arquivo da temporada já existe, ele é lido do cache. "
             "Se não, a função chama o endpoint da NBA, filtrando a temporada regular e os dados por time. Como a API "
             "às vezes recusa conexões ou demora, cada chamada passa por uma função de retry, que tenta de novo com uma espera "
             "que dobra a cada falha. Para atualizar a temporada atual, basta rodar a coleta com a opção refresh current.",
             "This is the core of the collection, in coleta dot py. If the season file already exists, it is read from the cache. "
             "If not, the function calls the NBA endpoint, filtering the regular season and team-level data. Since the API "
             "sometimes refuses connections or times out, every call goes through a retry function that tries again with a wait "
             "that doubles after each failure. To update the current season, you just run the collection with the refresh current option.")),

    dict(kind="table", eyebrow=L("BASE PROCESSADA", "PROCESSED DATA"),
         title=L("games.csv: 38.734 linhas, uma por time por jogo", "games.csv: 38,734 rows, one per team per game"),
         header=["SEASON", "TEAM", "GAME_DATE", "OPP", "HOME", "WIN", "PTS", "OPP_PTS", "FGA", "FTA", "OREB", "TOV"],
         rows=[["2010-11", "ATL", "2010-10-27", "MEM", "0", "1", "119", "104", "80", "31", "9", "15"],
               ["2010-11", "ATL", "2010-10-29", "PHI", "0", "1", "104", "101", "70", "31", "10", "20"],
               ["…", "…", "…", "…", "…", "…", "…", "…", "…", "…", "…", "…"],
               ["2026-27", "PHI", "2026-11-21", "…", "…", "…", "…", "…", "…", "…", "…", "…"]],
         foot=L("16 temporadas históricas (2010-11 a 2025-26) × 30 times = 480 times-temporada",
                "16 historical seasons (2010-11 to 2025-26) × 30 teams = 480 team-seasons"),
         say=L(
             "Depois da coleta, os game logs viram uma base única, o games ponto csv, com trinta e oito mil setecentas e trinta e quatro linhas. "
             "Cada jogo aparece duas vezes, uma para cada time, e na mesma linha juntamos as estatísticas do adversário, "
             "porque elas são necessárias para estimar as posses de bola. A base histórica tem dezesseis temporadas completas, "
             "de 2010 a 2026. Com trinta times, são quatrocentos e oitenta times-temporada. Cada time em cada temporada é uma observação. "
             "Isso é pouco para aprendizado de máquina, e essa limitação vai influenciar a escolha dos modelos.",
             "After collection, the game logs become a single table, games dot csv, with thirty-eight thousand seven hundred thirty-four rows. "
             "Each game appears twice, once for each team, and on the same row we join the opponent's stats, "
             "because they are needed to estimate possessions. The historical data has sixteen complete seasons, "
             "from 2010 to 2026. With thirty teams, that makes four hundred eighty team-seasons. Each team in each season is one observation. "
             "That is small for machine learning, and this limitation will shape the choice of models.")),

    dict(kind="code", file="src/features.py", start=48,
         code='''def build_features(games: pd.DataFrame, n: int) -> pd.DataFrame:
    g = games.sort_values(["SEASON", "TEAM", "GAME_DATE", "GAME_ID"])
    g["k"] = g.groupby(["SEASON", "TEAM"]).cumcount() + 1  # nº do jogo
    first = g[g["k"] <= n].copy()          # só os N primeiros jogos

    agg = first.groupby(["SEASON", "TEAM"]).agg(
        gp=("WIN", "size"), wins=("WIN", "sum"),
        pf=("PTS", "sum"), pa=("OPP_PTS", "sum"), poss=("poss", "sum"))
    agg["win_pct"] = agg.wins / agg.gp
    agg["pd_pg"]   = (agg.pf - agg.pa) / agg.gp
    agg["net_rtg"] = 100 * (agg.pf - agg.pa) / agg.poss
    agg["pyth"]    = 1.0 / (1.0 + (agg.pa / agg.pf) ** 14)
    # força de tabela: adversários só até a data de corte do time
    # alvo: aproveitamento FINAL da temporada''',
         eyebrow=L("FASE 2 · FEATURES", "PHASE 2 · FEATURES"),
         title=L("Tudo cortado no 15º jogo", "Everything cut at game 15"),
         notes=[L("Sem vazamento: nada depois do N-ésimo jogo", "No leakage: nothing after game N"),
                L("Posses = FGA + 0,44·FTA − OREB + TOV", "Possessions = FGA + 0.44·FTA − OREB + TOV"),
                L("N = menor nº de jogos de um time hoje", "N = fewest games any team has played today")],
         say=L(
             "Na fase dois, o arquivo features ponto py transforma os jogos em variáveis de entrada. O ponto principal está "
             "na terceira linha: numeramos os jogos de cada time e guardamos só os N primeiros. N é o menor número de jogos "
             "disputados por um time hoje, que dá quinze. Isso evita vazamento de dados, ou seja, usar sem querer uma informação "
             "que não existiria no dia da previsão. Até a força de tabela é calculada só com jogos até a data de corte de cada time. "
             "As posses de bola são estimadas pela fórmula clássica: arremessos tentados, mais zero vírgula quarenta e quatro vezes "
             "os lances livres, menos os rebotes ofensivos, mais os erros.",
             "In phase two, features dot py turns the games into input variables. The key point is on the third line: "
             "we number each team's games and keep only the first N. N is the fewest games any team has played today, which is fifteen. "
             "This prevents data leakage, that is, accidentally using information that would not exist on the day of the forecast. "
             "Even strength of schedule is computed only with games up to each team's cutoff date. "
             "Possessions are estimated with the classic formula: field goal attempts, plus zero point four four times "
             "free throw attempts, minus offensive rebounds, plus turnovers.")),

    dict(kind="table", eyebrow=L("AS SEIS FEATURES", "THE SIX FEATURES"),
         title=L("Exemplo: Philadelphia nos 15 primeiros jogos", "Example: Philadelphia in its first 15 games"),
         header=[L("Feature", "Feature"), L("O que mede", "What it measures"), "PHI"],
         rows=[[L("Aproveitamento", "Win %"), L("vitórias / jogos", "wins / games"), L("0,800", "0.800")],
               [L("Saldo por jogo", "Point diff. per game"), L("(pontos feitos − sofridos) / jogos", "(points for − against) / games"), L("+2,8", "+2.8")],
               ["Net rating", L("saldo a cada 100 posses", "point diff. per 100 possessions"), L("+2,7", "+2.7")],
               ["Pythagorean", L("vitórias “merecidas” pelos pontos", "wins “deserved” by points"), L("0,586", "0.586")],
               [L("Força de tabela", "Strength of schedule"), L("aproveitamento dos adversários", "opponents' win %"), L("0,460", "0.460")],
               [L("Temporada anterior", "Previous season"), L("aproveitamento final do ano passado", "last year's final win %"), L("0,549", "0.549")]],
         foot=L("Alvo: aproveitamento final (erros convertidos para vitórias × 82)",
                "Target: final win % (errors converted to wins × 82)"),
         say=L(
             "São seis features. O aproveitamento, vitórias divididas por jogos. O saldo de pontos por jogo. O net rating, "
             "que é o saldo a cada cem posses e corrige o ritmo de jogo. A expectativa pitagórica, que estima as vitórias "
             "merecidas pelos pontos feitos e sofridos. A força de tabela, o aproveitamento médio dos adversários. "
             "E o aproveitamento da temporada anterior. Veja o Philadelphia: zero vírgula oitocentos de aproveitamento nos quinze "
             "primeiros jogos, mas só zero vírgula quinhentos e oitenta e seis pela pitagórica. O alvo é o aproveitamento final, "
             "e não o número de vitórias, porque três temporadas tiveram menos de oitenta e dois jogos. "
             "Para facilitar a leitura, os erros são convertidos para vitórias, multiplicando por oitenta e dois.",
             "There are six features. Win percentage, wins divided by games. Point differential per game. Net rating, "
             "the point differential per hundred possessions, which corrects for pace. The Pythagorean expectation, which estimates "
             "the wins a team deserves from points scored and allowed. Strength of schedule, the opponents' average win percentage. "
             "And the previous season's win percentage. Look at Philadelphia: a point eight hundred win percentage in its first fifteen games, "
             "but only point five eight six by the Pythagorean formula. The target is the final win percentage, "
             "not the number of wins, because three seasons had fewer than eighty-two games. "
             "To make it easier to read, errors are converted to wins by multiplying by eighty-two.")),

    dict(kind="figure", img="correlacao_features.png", layout="side",
         eyebrow=L("ANÁLISE EXPLORATÓRIA", "EXPLORATORY ANALYSIS"),
         title=L("Features quase redundantes", "Nearly redundant features"),
         notes=[L("Saldo × net rating: 0,999", "Point diff. × net rating: 0.999"),
                L("As de pontos passam de 0,99 entre si", "Points-based features exceed 0.99"),
                L("Isso vai pesar na escolha do Ridge", "This will matter when choosing Ridge")],
         say=L(
             "Antes de modelar, olhamos a correlação entre as features. As três baseadas em pontos, saldo, net rating e pitagórica, "
             "têm correlação acima de zero vírgula noventa e nove entre si. Saldo e net rating chegam a zero vírgula novecentos e noventa e nove: "
             "são praticamente a mesma informação. Isso se chama multicolinearidade, e vai ser decisivo na escolha do modelo.",
             "Before modeling, we looked at the correlation between features. The three points-based ones, point differential, "
             "net rating and Pythagorean, correlate above point nine nine with each other. Point differential and net rating reach "
             "point nine nine nine: they are practically the same information. This is called multicollinearity, and it will be decisive "
             "when choosing the model.")),

    # ------------------------------------------------------------------ 3. metodologia
    dict(kind="section", num="03", title=L("Metodologia", "Methodology"),
         sub=L("Modelos, validação e simulação", "Models, validation and simulation"),
         say=L("Terceira parte: a metodologia.", "Part three: the methodology.")),

    dict(kind="pipeline", eyebrow=L("PIPELINE", "PIPELINE"),
         title=L("Sete scripts, um notebook", "Seven scripts, one notebook"),
         steps=[("coleta.py", L("API da NBA → cache", "NBA API → cache")),
                ("features.py", L("6 features, N = 15", "6 features, N = 15")),
                ("modelos.py", L("baselines + 4 modelos", "baselines + 4 models")),
                ("simulacao.py", L("Monte Carlo + backtest", "Monte Carlo + backtest")),
                ("versoes.py", L("V0 · V5 · V10 · V15", "V0 · V5 · V10 · V15")),
                ("sensibilidade.py", L("erro × nº de jogos", "error × games played")),
                ("resumo.py", L("results/resumo.md", "results/resumo.md"))],
         foot=L("notebooks/projeto.ipynb roda tudo, na ordem · seed fixa 42 · figuras em PT e EN",
                "notebooks/projeto.ipynb runs everything in order · fixed seed 42 · figures in PT and EN"),
         say=L(
             "O trabalho foi organizado como um pipeline de sete scripts Python, um por fase. Coleta, features, modelos, simulação, "
             "versões, sensibilidade e resumo. O notebook projeto ponto ipynb chama esses scripts na ordem e roda o pipeline inteiro, "
             "com explicações entre as etapas. A semente aleatória é fixa em quarenta e dois, para que tudo seja reproduzível, "
             "e todas as figuras são geradas em português e em inglês. No final, outro script gera as tabelas do artigo e outro monta os slides.",
             "The work is organized as a pipeline of seven Python scripts, one per phase: collection, features, models, simulation, "
             "versions, sensitivity and summary. The projeto dot ipynb notebook calls these scripts in order and runs the whole pipeline, "
             "with explanations between steps. The random seed is fixed at forty-two so everything is reproducible, "
             "and every figure is generated in Portuguese and in English. At the end, one script builds the paper's tables and another builds the slides.")),

    dict(kind="slide", n=4, say=L(
        "Este gráfico é o centro do trabalho. Cada ponto é um time-temporada. No eixo horizontal, o aproveitamento depois "
        "de quinze jogos; no vertical, o aproveitamento final. Se o começo dissesse tudo, os pontos estariam na diagonal tracejada. "
        "Não estão. A reta ajustada tem inclinação zero vírgula sessenta e três: cada ponto acima de zero vírgula quinhentos "
        "no começo vale só sessenta e três por cento no fim. É a regressão à média: um time que começa doze a três provavelmente "
        "teve um pouco de sorte. O desvio-padrão também cai, de zero vírgula dezenove depois de quinze jogos para zero vírgula quinze "
        "no fim. Conclusão: qualquer previsão boa precisa encolher o começo em direção à média.",
        "This chart is the heart of the project. Each dot is a team-season. On the horizontal axis, the win percentage after "
        "fifteen games; on the vertical axis, the final win percentage. If the start told the whole story, the dots would sit on the dashed diagonal. "
        "They don't. The fitted line has a slope of point six three: every point above five hundred at the start is worth only "
        "sixty-three percent by the end. This is regression to the mean: a team that starts twelve and three probably got a bit lucky. "
        "The standard deviation also shrinks, from point one nine after fifteen games to point one five at the end. "
        "Conclusion: any good forecast has to shrink the start toward the mean.")),

    dict(kind="slide", n=5, say=L(
        "Comparamos dois baselines, que servem de régua, com quatro modelos. O primeiro baseline supõe que o time mantém o "
        "aproveitamento atual até o fim. O segundo usa a fórmula pitagórica, com expoente catorze. Os modelos são a regressão linear "
        "por mínimos quadrados; o Ridge, que é a regressão linear com uma penalidade L2 sobre o tamanho dos coeficientes, controlada "
        "pelo parâmetro alfa; o Lasso, com penalidade L1, que pode zerar coeficientes; e uma Random Forest de quinhentas árvores, "
        "com pelo menos dez times por folha, para não decorar os dados. As features são padronizadas antes do treino.",
        "We compared two baselines, which act as a yardstick, with four models. The first baseline assumes the team keeps its "
        "current win percentage until the end. The second uses the Pythagorean formula, with an exponent of fourteen. The models are ordinary "
        "least squares linear regression; Ridge, which is linear regression with an L2 penalty on the size of the coefficients, controlled "
        "by the alpha parameter; Lasso, with an L1 penalty, which can set coefficients to zero; and a Random Forest with five hundred trees "
        "and at least ten teams per leaf, so it does not memorize the data. Features are standardized before training.")),

    dict(kind="slide", n=6, say=L(
        "Para não nos enganarmos, toda métrica é medida em dados que o modelo não viu. Usamos o leave-one-season-out: "
        "tiramos uma temporada inteira, treinamos com as outras quinze e prevemos a que ficou de fora, dezesseis vezes. "
        "Separar por temporada, e não por time, é importante, porque times da mesma temporada dividem as mesmas condições. "
        "Também fizemos um holdout temporal: treino até 2023 e teste nas três temporadas mais recentes. "
        "E o alfa do Ridge é escolhido numa validação interna, também por temporada, para que o teste nunca influencie a escolha.",
        "To avoid fooling ourselves, every metric is measured on data the model has not seen. We used leave-one-season-out: "
        "we remove a whole season, train on the other fifteen and predict the one left out, sixteen times. "
        "Splitting by season rather than by team matters, because teams in the same season share the same conditions. "
        "We also ran a temporal holdout: training up to 2023 and testing on the three most recent seasons. "
        "And Ridge's alpha is chosen in an inner validation, also split by season, so the test set never influences the choice.")),

    dict(kind="code", file="src/modelos.py", start=59,
         code='''def _one_se_rule(cv_results):
    """Maior alpha cujo erro de CV está a até 1 erro-padrão do mínimo."""
    err = -cv_results["mean_test_score"]
    se = cv_results["std_test_score"] / np.sqrt(n_splits)
    best = int(np.argmin(err))
    ok = np.where(err <= err[best] + se[best])[0]
    return int(ok.max())          # o modelo mais simples entre os empatados


class Tuned:
    """GridSearchCV com GroupKFold por temporada (sem vazamento entre anos)."""
    def fit(self, X, y, groups):
        self.gs_ = GridSearchCV(self.estimator, self.param_grid,
                                cv=GroupKFold(n),
                                scoring="neg_mean_absolute_error",
                                refit=_one_se_rule)
        self.gs_.fit(X, y, groups=groups)
        return self''',
         eyebrow=L("FASE 3 · MODELOS", "PHASE 3 · MODELS"),
         title=L("Busca aninhada e regra de 1 erro-padrão", "Nested search and the one-standard-error rule"),
         notes=[L("GroupKFold: grupos = temporadas", "GroupKFold: groups = seasons"),
                L("Métrica: erro absoluto médio", "Metric: mean absolute error"),
                L("Resultado: α = 100", "Result: α = 100")],
         say=L(
             "No código, isso aparece em modelos ponto py. A classe Tuned faz uma busca em grade com GroupKFold, em que os grupos são as temporadas, "
             "e mede o erro absoluto médio. Em vez de pegar o alfa com o menor erro, usamos a regra de um erro-padrão: entre todos os alfas "
             "cujo erro fica a até um erro-padrão do melhor, escolhemos o maior, que é o modelo mais simples e estável. "
             "Se dois modelos estão estatisticamente empatados, ficamos com o mais conservador. O alfa escolhido foi cem.",
             "In the code, this lives in modelos dot py. The Tuned class runs a grid search with GroupKFold, where the groups are seasons, "
             "and measures mean absolute error. Instead of taking the alpha with the lowest error, we use the one-standard-error rule: among all alphas "
             "whose error is within one standard error of the best, we pick the largest, which is the simplest and most stable model. "
             "If two models are statistically tied, we keep the more conservative one. The chosen alpha was one hundred.")),

    dict(kind="slide", n=9, say=L(
        "A regressão prevê o aproveitamento final, mas o objetivo são as chances de top seis. Para isso, a previsão do Ridge vira o rating, "
        "a força de cada time. O San Antonio tem rating zero vírgula setecentos e vinte e sete, e o Philadelphia, com a mesma campanha, "
        "só zero vírgula quinhentos e noventa e dois, porque o saldo dele é bem menor. Uma regressão logística, treinada nos jogos históricos, "
        "transforma a diferença de rating e o mando de quadra na chance de vitória em cada jogo. Entre times iguais, o mandante vence cinquenta "
        "e oito por cento das vezes. Cada rating ainda ganha um ruído com desvio sigma de zero vírgula zero oitenta e cinco, cerca de sete vitórias, "
        "porque não conhecemos a força real de ninguém com certeza.",
        "The regression predicts the final win percentage, but the goal is the odds of making the top six. For that, the Ridge forecast becomes the rating, "
        "each team's strength. San Antonio has a rating of point seven two seven, and Philadelphia, with the same record, "
        "only point five nine two, because its point differential is much smaller. A logistic regression, trained on historical games, "
        "turns the rating difference and home court into a win probability for each game. Between equal teams, the home team wins fifty-eight "
        "percent of the time. Each rating also gets random noise with a standard deviation, sigma, of point zero eight five, about seven wins, "
        "because we never know any team's true strength for sure.")),

    dict(kind="code", file="src/simulacao.py", start=76,
         code='''def simulate(teams, conf, rating, cur_wins, cur_gp, home_idx,
             away_idx, coef, sigma, n_sims=N_SIMS, seed=SEED):
    rng = np.random.default_rng(seed)
    b_diff, b_home = coef
    # incerteza do rating: um ruído por time em cada simulação
    r = rating[None, :] + rng.normal(0, sigma, size=(n_sims, T))
    wins = np.repeat(cur_wins[None, :].astype(float), n_sims, axis=0)

    # os 952 jogos que faltam, sorteados pelo modelo logístico
    logit = b_diff * (r[:, home_idx] - r[:, away_idx]) + b_home
    home_win = rng.random(logit.shape) < 1 / (1 + np.exp(-logit))
    np.add.at(wins.T, home_idx, home_win.T)
    np.add.at(wins.T, away_idx, (~home_win).T)

    # classificação por conferência (desempate aleatório)
    ...
    return wins, pos''',
         eyebrow=L("FASE 4 · SIMULAÇÃO", "PHASE 4 · SIMULATION"),
         title=L("10.000 temporadas sorteadas", "10,000 simulated seasons"),
         notes=[L("logit = 4,35·Δrating + 0,32·mando", "logit = 4.35·Δrating + 0.32·home"),
                L("Vetorizado em NumPy: 10.000 × 952 jogos", "Vectorized in NumPy: 10,000 × 952 games"),
                L("2 jogos da NBA Cup: adversário médio", "2 NBA Cup games: average opponent")],
         say=L(
             "Esta é a simulação de Monte Carlo, em simulacao ponto py. Em vez de calcular as probabilidades por fórmula, sorteamos o resto da temporada "
             "dez mil vezes. Primeiro, cada time recebe um ruído no rating. Depois, para cada um dos novecentos e cinquenta e dois jogos restantes, "
             "o modelo logístico dá a chance de o mandante vencer, e um número aleatório decide o jogo. Tudo é vetorizado em NumPy, "
             "então as dez mil temporadas rodam em segundos. Somamos as vitórias atuais, montamos a classificação de cada conferência e contamos: "
             "a probabilidade de top seis de um time é a fração das simulações em que ele terminou entre os seis primeiros. "
             "Os dois jogos da NBA Cup que ainda não têm adversário são simulados contra um time médio, em quadra neutra.",
             "This is the Monte Carlo simulation, in simulacao dot py. Instead of computing the probabilities with a formula, we draw the rest of the season "
             "ten thousand times. First, each team gets noise on its rating. Then, for each of the nine hundred fifty-two remaining games, "
             "the logistic model gives the home team's chance of winning, and a random number decides the game. Everything is vectorized in NumPy, "
             "so ten thousand seasons run in seconds. We add the current wins, build each conference's standings and count: "
             "a team's top six probability is the share of simulations in which it finished in the top six. "
             "The two NBA Cup games that do not have an opponent yet are simulated against an average team, on a neutral court.")),

    dict(kind="slide", n=10, say=L(
        "Mas dá para confiar nessas chances? Para responder, fizemos um backtest. Para cada uma das dezesseis temporadas passadas, voltamos ao dia "
        "em que o último time completou quinze jogos e simulamos o resto, sem usar aquela temporada no treino. Depois comparamos com o que aconteceu. "
        "O intervalo de oitenta por cento conteve as vitórias reais em oitenta e um por cento dos casos: a incerteza está bem medida. "
        "E o Brier score, que mede o erro das probabilidades, foi zero vírgula quarenta e dois, contra zero vírgula sessenta e seis de quem chuta "
        "sempre as proporções fixas. Quanto menor, melhor.",
        "But can we trust these odds? To answer that, we ran a backtest. For each of the sixteen past seasons, we went back to the day "
        "the last team completed fifteen games and simulated the rest, without using that season in training. Then we compared it with what actually happened. "
        "The eighty percent interval contained the actual wins in eighty-one percent of cases: the uncertainty is well measured. "
        "And the Brier score, which measures the error of the probabilities, was point four two, against point six six for always guessing "
        "the fixed proportions. Lower is better.")),

    dict(kind="figure", img="calibracao_simulacao.png", layout="side",
         eyebrow=L("CALIBRAÇÃO", "CALIBRATION"),
         title=L("Quando diz 30%, acontece ~30%", "When it says 30%, it happens ~30%"),
         notes=[L("Backtest fora da amostra, 16 temporadas", "Out-of-sample backtest, 16 seasons"),
                L("Pontos perto da diagonal = bem calibrado", "Points near the diagonal = well calibrated"),
                L("Cobertura do IC80: 81%", "80% interval coverage: 81%")],
         say=L(
             "A curva de calibração mostra o mesmo de outro jeito. Agrupamos as previsões do backtest por faixa de probabilidade e comparamos com a "
             "frequência real. Os pontos ficam perto da diagonal: quando a simulação diz trinta por cento, o evento acontece mais ou menos trinta por cento das vezes.",
             "The calibration curve shows the same thing another way. We grouped the backtest forecasts by probability bin and compared them with the "
             "actual frequency. The points sit close to the diagonal: when the simulation says thirty percent, the event happens about thirty percent of the time.")),

    dict(kind="cards", eyebrow=L("ANÁLISES COMPLEMENTARES", "ADDITIONAL ANALYSES"),
         title=L("Quanto cada bloco de jogos acrescenta?", "How much does each block of games add?"),
         cards=[
             ("V0", L("19/10 · pré-temporada", "Oct 19 · preseason"), L("Só a temporada anterior.", "Previous season only.")),
             ("V5", L("02/11 · 5 jogos", "Nov 2 · 5 games"), L("Pipeline inteiro refeito.", "Whole pipeline redone.")),
             ("V10", L("11/11 · 10 jogos", "Nov 11 · 10 games"), L("Novo Ridge, σ e backtest.", "New Ridge, σ and backtest.")),
             ("V15", L("22/11 · 15 jogos", "Nov 22 · 15 games"), L("A versão atual.", "The current version.")),
         ],
         foot=L("sensibilidade.py: o mesmo LOSO com N = 5, 10, 15, 20, 25, 30 e 41 jogos",
                "sensibilidade.py: the same LOSO with N = 5, 10, 15, 20, 25, 30 and 41 games"),
         say=L(
             "Duas análises completam a metodologia. Nas versões, o pipeline inteiro, com features, Ridge, modelo de jogo, sigma, backtest e simulação, "
             "é refeito em quatro datas da temporada, cada uma só com o que se sabia naquele dia: antes da estreia, e depois de cinco, dez e quinze jogos. "
             "E na análise de sensibilidade repetimos a validação com N de cinco a quarenta e um jogos, para ver como o erro cai com mais informação.",
             "Two analyses complete the methodology. In the versions, the whole pipeline, with features, Ridge, game model, sigma, backtest and simulation, "
             "is redone at four dates in the season, each using only what was known that day: before opening night, and after five, ten and fifteen games. "
             "And in the sensitivity analysis we repeat the validation with N from five to forty-one games, to see how the error drops with more information.")),

    # ------------------------------------------------------------------ 4. resultados
    dict(kind="section", num="04", title=L("Resultados e análises", "Results and analysis"),
         sub=L("O que os números mostram", "What the numbers show"),
         say=L("Quarta parte: os resultados e as análises.", "Part four: the results and the analysis.")),

    dict(kind="slide", n=7, say=L(
        "O resultado principal. Manter o aproveitamento atual erra, em média, sete vírgula seis vitórias por time. O Ridge erra cinco vírgula seis. "
        "São duas vitórias a menos, e duas vitórias muitas vezes separam o sexto do sétimo lugar. No holdout das temporadas recentes, o Ridge erra "
        "ainda menos: cinco vírgula trinta e cinco. A correlação de Spearman, que mede se a ordem prevista bate com a real, sobe de zero vírgula setenta e quatro "
        "para zero vírgula setenta e oito. E um detalhe importante: regressão linear, Ridge, Lasso e Random Forest ficaram empatados dentro de um erro-padrão, "
        "de zero vírgula vinte e cinco vitória. Ou seja, o ganho vem de encolher o começo, não de escolher o algoritmo.",
        "The main result. Keeping the current win percentage misses by seven point six wins per team, on average. Ridge misses by five point six. "
        "That is two wins fewer, and two wins often separate sixth place from seventh. On the holdout of recent seasons, Ridge does "
        "even better: five point three five. Spearman correlation, which measures whether the predicted order matches the real one, rises from point seven four "
        "to point seven eight. And an important detail: linear regression, Ridge, Lasso and Random Forest are tied within one standard error, "
        "a quarter of a win. In other words, the gain comes from shrinking the start, not from picking the algorithm.")),

    dict(kind="figure", img="previsto_vs_real.png", layout="wide",
         eyebrow=L("PREVISTO × REAL", "PREDICTED × ACTUAL"),
         title=L("Baseline espalhado, Ridge perto da diagonal", "Baseline scattered, Ridge near the diagonal"),
         say=L(
             "Aqui está a comparação visual entre o baseline e o modelo, nas previsões fora da amostra. À esquerda, manter o aproveitamento gera "
             "previsões espalhadas demais, com começos extremos levados ao pé da letra. À direita, o Ridge comprime as previsões em direção à média, "
             "e os pontos ficam mais perto da diagonal.",
             "Here is the visual comparison between the baseline and the model, on out-of-sample predictions. On the left, keeping the win percentage produces "
             "predictions that are far too spread out, taking extreme starts at face value. On the right, Ridge compresses the predictions toward the mean, "
             "and the points sit closer to the diagonal.")),

    dict(kind="figure", img="coeficientes_ridge.png", layout="wide",
         eyebrow=L("POR QUE RIDGE", "WHY RIDGE"),
         title=L("Mesmo erro, coeficientes que fazem sentido", "Same error, coefficients that make sense"),
         say=L(
             "Por que escolher o Ridge, se a regressão linear teve erro um pouco menor? Por causa dos coeficientes. Com saldo e net rating quase idênticos, "
             "a regressão linear dá mais zero vírgula dezesseis para um e menos zero vírgula dezoito para o outro. Isso diria que um time com saldo melhor "
             "por posse é pior, o que não faz sentido: é o modelo compensando um coeficiente com o outro. O Ridge divide o peso igualmente entre as três "
             "features de pontos, cerca de zero vírgula zero dois três cada. A força de tabela quase não pesa. Mesmo erro, mas coeficientes interpretáveis e estáveis.",
             "Why choose Ridge if linear regression had a slightly lower error? Because of the coefficients. With point differential and net rating almost identical, "
             "linear regression gives plus point one six to one and minus point one eight to the other. That would say a team with a better differential "
             "per possession is worse, which makes no sense: it is the model offsetting one coefficient with the other. Ridge splits the weight evenly across the three "
             "points-based features, about point zero two three each. Strength of schedule barely counts. Same error, but interpretable, stable coefficients.")),

    dict(kind="figure", img="sensibilidade_n.png", layout="side",
         eyebrow=L("SENSIBILIDADE", "SENSITIVITY"),
         title=L("O modelo ajuda mais quando há menos jogos", "The model helps most when there are fewer games"),
         notes=[L("N = 5: baseline 13,3 · Ridge 7,2", "N = 5: baseline 13.3 · Ridge 7.2"),
                L("N = 15: 7,6 · 5,6", "N = 15: 7.6 · 5.6"),
                L("N = 41: 3,9 · 3,6", "N = 41: 3.9 · 3.6")],
         say=L(
             "A análise de sensibilidade mostra quando o modelo é mais útil. Com só cinco jogos, manter o aproveitamento erra treze vírgula três vitórias, "
             "porque o começo é quase puro ruído. O Ridge erra sete vírgula dois, quase a metade. Conforme a temporada avança, as duas curvas se aproximam: "
             "com quarenta e um jogos, a diferença é pequena. O modelo vale mais justamente quando há menos informação.",
             "The sensitivity analysis shows when the model helps most. With only five games, keeping the win percentage misses by thirteen point three wins, "
             "because the start is almost pure noise. Ridge misses by seven point two, almost half. As the season goes on, the two curves get closer: "
             "at forty-one games, the gap is small. The model is worth the most exactly when there is the least information.")),

    dict(kind="figure", img="versoes_backtest.png", layout="wide",
         eyebrow=L("VERSÕES", "VERSIONS"),
         title=L("Cada bloco de 5 jogos melhora a previsão", "Each block of 5 games improves the forecast"),
         say=L(
             "Nas versões, o backtest de cada data mostra a melhora. O Brier cai de zero vírgula cinquenta e três na pré-temporada para zero vírgula quarenta e nove "
             "com cinco jogos, zero vírgula quarenta e quatro com dez e zero vírgula quarenta e dois com quinze. O erro nas vitórias finais cai de sete vírgula oito "
             "para cinco vírgula três. A linha tracejada é a referência de não saber nada. A cobertura do intervalo de oitenta por cento fica perto de oitenta "
             "a partir da versão de cinco jogos; na pré-temporada é de oitenta e sete, porque o modelo sabe pouco e os intervalos ficam largos.",
             "In the versions, each date's backtest shows the improvement. The Brier score drops from point five three in the preseason to point four nine "
             "with five games, point four four with ten and point four two with fifteen. The error in final wins drops from seven point eight "
             "to five point three. The dashed line is the reference of knowing nothing. Coverage of the eighty percent interval stays near eighty "
             "from the five-game version on; in the preseason it is eighty-seven, because the model knows little and the intervals are wide.")),

    dict(kind="figure", img="versoes_trajetoria.png", layout="wide",
         eyebrow=L("TRAJETÓRIAS", "TRAJECTORIES"),
         title=L("Times mudando de patamar", "Teams changing tiers"),
         say=L(
             "E dá para ver times mudando de patamar ao longo das versões. O Memphis, que vinha de vinte e cinco vitórias, começou onze a quatro com saldo forte: "
             "saiu de trinta e três para quarenta e oito vitórias esperadas, e a chance de top seis foi de catorze para quarenta e oito por cento. "
             "Já o Toronto subiu para quarenta e nove na versão de cinco jogos e caiu para trinta e oito na de quinze: um bom começo que não se sustentou. "
             "Por isso não dá para confiar numa foto só.",
             "And you can see teams changing tiers across the versions. Memphis, coming off twenty-five wins, started eleven and four with a strong point differential: "
             "it went from thirty-three to forty-eight expected wins, and its top six chance went from fourteen to forty-eight percent. "
             "Toronto, on the other hand, rose to forty-nine in the five-game version and fell to thirty-eight in the fifteen-game one: a good start that did not last. "
             "That is why you cannot trust a single snapshot.")),

    dict(kind="figure", img="heatmap_posicoes.png", layout="wide",
         eyebrow=L("PROJEÇÃO 2026-27", "2026-27 PROJECTION"),
         title=L("Onde cada time termina, em 10.000 simulações", "Where each team finishes, in 10,000 simulations"),
         say=L(
             "Esta é a projeção atual. No mapa de calor, cada linha é um time e cada coluna uma posição final, de um a quinze. O número é a porcentagem das "
             "simulações em que o time terminou naquela posição. A linha contínua marca o corte do top seis, e a tracejada, o do play-in. "
             "No topo, as distribuições ficam concentradas; no meio da tabela, espalhadas por várias posições, que é onde está a incerteza de verdade.",
             "This is the current projection. In the heatmap, each row is a team and each column a final position, from one to fifteen. The number is the share of "
             "simulations in which the team finished in that position. The solid line marks the top six cutoff, and the dashed line the play-in cutoff. "
             "At the top, the distributions are concentrated; in the middle of the table they spread over several positions, which is where the real uncertainty is.")),

    dict(kind="slide", n=12, say=L(
        "Alguns destaques. Boston tem noventa e sete por cento de chance de top seis, e San Antonio, noventa e cinco, com cinquenta e nove vitórias esperadas. "
        "E o Philadelphia, com catorze a três? Mantida a campanha, seriam umas sessenta e sete vitórias. O modelo projeta cinquenta e duas vírgula quatro, "
        "com intervalo de quarenta e quatro a sessenta, porque o saldo de mais dois vírgula oito por jogo é de um time bom, não de um candidato ao título. "
        "As vitórias já conquistadas contam; o que o modelo encolhe é o ritmo daqui para frente. O Boston, com campanha pior, tem chance maior: saldo de "
        "mais dez vírgula cinco por jogo e boa temporada anterior. O Memphis está no limite, com quarenta e oito por cento de top seis e quarenta e seis de play-in.",
        "Some highlights. Boston has a ninety-seven percent chance of a top six finish, and San Antonio ninety-five, with fifty-nine expected wins. "
        "And Philadelphia, at fourteen and three? At that pace it would win about sixty-seven games. The model projects fifty-two point four, "
        "with an interval from forty-four to sixty, because a plus two point eight per game differential belongs to a good team, not a title contender. "
        "The wins already banked count; what the model shrinks is the pace from here on. Boston, with a worse record, has a better chance: a plus ten point five "
        "per game differential and a strong previous season. Memphis is on the edge, with forty-eight percent top six and forty-six percent play-in.")),

    dict(kind="slide", n=13, say=L(
        "O que aprendemos. Validar por temporada, sem vazamento, é o que torna os números confiáveis. Um modelo linear simples empatou com a floresta "
        "aleatória: com quatrocentas e oitenta observações e uma relação quase linear, um modelo complexo não tem o que aprender a mais. E testar a simulação "
        "no passado é o que mostra que as probabilidades fazem sentido. As limitações: lesões, trocas e mudanças de elenco não são modeladas, o rating usa só "
        "os quinze primeiros jogos de cada time e os desempates são sorteados, e não pelos critérios oficiais. Ficam como próximos passos, junto com novas "
        "versões de vinte, vinte e cinco e trinta jogos.",
        "What we learned. Validating by season, without leakage, is what makes the numbers trustworthy. A simple linear model tied with the random forest: "
        "with four hundred eighty observations and an almost linear relationship, a complex model has nothing more to learn. And testing the simulation "
        "on the past is what shows the probabilities make sense. The limitations: injuries, trades and roster changes are not modeled, the rating uses only "
        "each team's first fifteen games, and ties are broken at random rather than by the official rules. These are the next steps, along with new "
        "versions at twenty, twenty-five and thirty games.")),

    dict(kind="cards", eyebrow=L("O QUE FOI CONSTRUÍDO", "WHAT WE BUILT"),
         title=L("Entregáveis", "Deliverables"),
         cards=[
             (L("CÓDIGO", "CODE"), "projeto.ipynb", L("Pipeline completo + 7 scripts em src/.", "Full pipeline + 7 scripts in src/.")),
             (L("ARTIGO", "PAPER"), L("IEEE · PT e EN", "IEEE · PT and EN"), L("LaTeX, tabelas geradas de results/, zip para o Overleaf.", "LaTeX, tables generated from results/, Overleaf zip.")),
             (L("APRESENTAÇÃO", "SLIDES"), L("14 slides · PT e EN", "14 slides · PT and EN"), L("HTML único, roteiro de fala e guia de termos.", "Single HTML file, talk script and glossary guide.")),
             (L("RESULTADOS", "RESULTS"), "results/", L("CSVs, figuras PT/EN e resumo.md.", "CSVs, PT/EN figures and resumo.md.")),
         ],
         say=L(
             "Para fechar, o que foi construído. O código, com o notebook que roda o pipeline inteiro e os sete scripts. Um artigo no formato IEEE, em português "
             "e em inglês, escrito em LaTeX, com as tabelas e figuras geradas direto dos resultados. A apresentação de catorze slides, nos dois idiomas, com o roteiro "
             "de fala e um guia que explica cada termo. E a pasta de resultados, com as tabelas, as figuras e um resumo. O código e os textos foram feitos com apoio "
             "do Claude, da Anthropic; os autores definiram a pergunta, os dados, os modelos e a validação, e conferiram os resultados.",
             "To wrap up, here is what we built. The code, with the notebook that runs the whole pipeline and the seven scripts. An IEEE-format paper, in Portuguese "
             "and English, written in LaTeX, with tables and figures generated straight from the results. The fourteen-slide presentation, in both languages, with the talk "
             "script and a guide that explains every term. And the results folder, with the tables, the figures and a summary. The code and texts were written with help "
             "from Claude, by Anthropic; the authors defined the question, the data, the models and the validation, and checked the results.")),

    dict(kind="slide", n=14, say=L(
        "A mensagem para levar é esta: confie na campanha, mas encolha antes. O começo da temporada tem informação, mas precisa ser puxado para a média "
        "e combinado com o saldo de pontos e a temporada anterior. E, como o projeto é vivo, é só rodar de novo para atualizar. Obrigado por assistir!",
        "The takeaway is this: trust the record, but shrink it first. The start of the season carries information, but it has to be pulled toward the mean "
        "and combined with point differential and the previous season. And since the project is live, you just rerun it to update. Thanks for watching!")),
]
