# Roteiro de fala — lightning talk (5 min)

Ritmo-alvo: ~130 palavras por minuto (~650 palavras no total). O tempo entre parênteses é a duração do slide; o tempo
à direita é o acumulado. **Negrito** = o que vale enfatizar. Se estiver atrasado, encurte os slides 5 e 6, que são os
mais fáceis de resumir.

---

### Slide 1 — Título (10 s) · 0:10
"Boa tarde. Nosso projeto se chama **quinze jogos não são uma temporada**: como prever a classificação final da NBA
quando a temporada mal começou."

### Slide 2 — A pergunta (15 s) · 0:25
"Hoje o Philadelphia está **14 a 3**. Isso é um time candidato ou só uma boa fase? A pergunta é: com uns 15 jogos,
qual vai ser o aproveitamento final de cada time, e qual a chance de terminar no top 6, no play-in ou fora?"

### Slide 3 — Dados (20 s) · 0:45
"Usamos a nba_api para baixar **16 temporadas**, 480 times-temporada. Para cada uma, calculamos seis features usando
**só os 15 primeiros jogos**: aproveitamento, saldo de pontos, net rating, Pythagorean, força de tabela e temporada
anterior. O alvo é o aproveitamento final, não vitórias, porque algumas temporadas tiveram menos de 82 jogos."

### Slide 4 — Regressão à média (30 s) · 1:15
"Este gráfico é a ideia central. No eixo x, o aproveitamento depois de 15 jogos; no y, o final. Se o começo fosse
confiável, os pontos estariam na diagonal. Mas a reta vermelha tem inclinação **0,63**: cada ponto acima de 0,500 no
começo vale só 63% no fim. Ou seja, o começo **regride à média**, e um bom modelo precisa encolher essas campanhas
extremas."

### Slide 5 — O que testamos (20 s) · 1:35
"Comparamos dois baselines: manter o aproveitamento atual e a fórmula Pythagorean. E quatro modelos: regressão linear,
**Ridge**, Lasso e Random Forest, todos com padronização dentro do pipeline."

### Slide 6 — Validação (20 s) · 1:55
"A unidade de validação é a **temporada**: deixamos uma temporada inteira de fora por vez, e também testamos nas três
mais recentes. O alpha do Ridge é escolhido por validação cruzada aninhada, também agrupada por temporada."

### Slide 7 — Resultados (25 s) · 2:20
"O resultado: manter o aproveitamento atual erra em média **7,6 vitórias**. O Ridge erra **5,6**. São duas vitórias
de erro a menos, e a ordem da classificação também melhora. Detalhe honesto: os quatro modelos ficaram empatados
dentro do erro-padrão. O que importa é encolher o começo, não o algoritmo."

### Slide 8 — Por que Ridge (25 s) · 2:45
"Então por que o Ridge? Saldo de pontos e net rating têm correlação de **0,999**. A regressão linear dá +0,16 para um
e −0,18 para o outro, o que não faz sentido. O Ridge divide o peso igualmente. **Mesmo erro, coeficientes que dá para
interpretar**: é a multicolinearidade que vimos em aula."

### Slide 9 — Simulação (25 s) · 3:10
"Para chegar às probabilidades, usamos a previsão do Ridge como rating de cada time. Uma regressão logística dá a
chance de vitória em cada jogo, a partir da diferença de rating e do mando. Aí simulamos os **952 jogos restantes
dez mil vezes**, com incerteza no rating."

### Slide 10 — Backtest (20 s) · 3:30
"Mas simulação só vale se for calibrada. Refizemos as 16 temporadas passadas, fora da amostra. O intervalo de 80%
acertou **81%** das vezes, e o Brier score caiu de 0,66 para 0,42. As probabilidades são confiáveis."

### Slide 11 — Projeção 2026-27 (30 s) · 4:00
"E esta é a projeção de hoje. Boston tem **97%** de chance de top 6, San Antonio **95%**. E o Philadelphia, que está
14 a 3? A projeção é de 52 vitórias, porque o saldo de pontos dele é modesto. O modelo segura o entusiasmo."

### Slide 12 — Lições (25 s) · 4:25
"O que funcionou: validar por temporada, sem vazamento, e testar a simulação em vez de confiar nela. O ganho é maior
bem no começo: com 5 jogos, o erro cai quase pela metade. Na próxima vez, queremos modelar lesões e trocas, atualizar
o rating a cada jogo e usar os critérios oficiais de desempate."

### Slide 13 — Encerramento (15 s) · 4:40
"Resumindo: **confie na campanha, mas encolha antes**. Regressão regularizada e simulação transformam 15 jogos
ruidosos em chances calibradas. O código está no notebook. Obrigado!"

*(~20 s de folga para perguntas ou atrasos.)*

---

## Perguntas prováveis (respostas curtas)

- **Por que não usar uma rede neural ou algo mais complexo?** Com 480 observações e uma relação quase linear, a Random
  Forest já não melhorou nada. Mais complexidade só aumentaria a variância.
- **Por que o Ridge, se a regressão linear teve MAE menor?** A diferença (0,12 vitória) é menor que o erro-padrão entre
  temporadas (0,25). Escolhemos o modelo mais estável, pela regra de um erro-padrão.
- **E lesões?** Não estão no modelo; é a principal limitação. O rating vem só dos resultados.
- **Por que 15 jogos?** É o menor número de jogos disputados por um time hoje. A análise de sensibilidade mostra o erro
  de N = 5 até 41.
- **O desempate é real?** Não, é aleatório. Os critérios oficiais da NBA ficaram como trabalho futuro.
