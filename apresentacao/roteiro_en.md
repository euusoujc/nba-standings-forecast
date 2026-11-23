# Talk script — lightning talk (5 min)

Target pace: ~140 words per minute (~640 words total). The time in parentheses is how long the slide stays up; the
time on the right is the running total. **Bold** = what to stress. If you are running late, shorten slides 5 and 6,
which are the easiest to summarize.

---

### Slide 1 — Title (10 s) · 0:10
"Good afternoon. Our project is called **fifteen games are not a season**. The idea is to predict how the NBA season
ends when it has barely started."

### Slide 2 — The question (15 s) · 0:25
"Philadelphia is **14 and 3**. Good team, or lucky? With about 15 games played, we want to know how many wins each team
ends up with, and its chance of finishing top six, in the play-in, or out."

### Slide 3 — Data (20 s) · 0:45
"Everything comes from the NBA's API: **16 seasons** of games, 480 team-seasons. For each
team we compute six numbers using **only the first 15 games**: win percentage, point differential, net rating,
Pythagorean, strength of schedule and last season."

### Slide 4 — Regression to the mean (25 s) · 1:10
"This chart is the heart of the project. On the x axis, win percentage after 15 games; on the y axis, at the end of the
season. If the start told you everything, the points would sit on the diagonal. They don't: the slope is **0.63**. Every
point above .500 early on is worth only 63% by the end. Early records **regress to the mean**, and the model has to
pull them back."

### Slide 5 — What we tested (15 s) · 1:25
"We compared two baselines, keeping the current win percentage and the Pythagorean formula, with four models: linear
regression, **Ridge**, Lasso and random forest."

### Slide 6 — Validation (15 s) · 1:40
"So we wouldn't fool ourselves, we left out a **whole season** at a time and tested on it. We also tested on just the
three most recent seasons. Ridge's alpha comes from an inner validation, also split by season."

### Slide 7 — Results (20 s) · 2:00
"Keeping the current win percentage misses by **7.6 wins** on average. Ridge misses by **5.6**. That's two wins better.
All four models tied within the standard error, so the gain comes from shrinking the start, not from the algorithm."

### Slide 8 — Why Ridge (20 s) · 2:20
"So why Ridge? Point differential and net rating correlate at **0.999**. Linear regression gives one +0.16 and the other
−0.18, which makes no sense. Ridge splits the weight. **Same error, and you can actually read the coefficients.**"

### Slide 9 — Simulation (20 s) · 2:40
"To get probabilities, the Ridge forecast becomes each team's rating. A logistic regression gives the win chance for
each game from the rating gap and home court. Then we simulate the **952 remaining games ten thousand times**."

### Slide 10 — Backtest (15 s) · 2:55
"And we tested that on the 16 past seasons, without peeking at the results. When the model says 80%, it's right **81%**
of the time. You can trust the odds."

### Slide 11 — Versions (30 s) · 3:25
"Then we redid the forecast **four times**: before opening night, and after 5, 10 and 15 games. Every five games the
error drops, from almost **8 wins** before the season to **5.3** now. You can also watch teams change tier. Memphis
went from 33 to 48 expected wins. Toronto rose to 49 and fell back to 38. That's why one snapshot isn't enough."

### Slide 12 — 2026-27 projection (25 s) · 3:50
"Here's today's projection: Boston has a **97%** chance of top six, San Antonio **95%**. And Philadelphia at 14 and 3?
It projects to 52 wins, because its point differential is modest."

### Slide 13 — Lessons (25 s) · 4:15
"What worked: validating by season and testing the simulation on the past before believing it. With only 5 games, the
error is already almost cut in half. Next time: model injuries and trades, keep adding versions through the season
and use the official tiebreakers."

### Slide 14 — Closing (20 s) · 4:35
"To sum up: **trust the record, but shrink it first**. And this is a living project: the data come from the NBA's API,
so you just rerun it to update. The code is in the notebook. Thank you!"

*(~25 s of slack for questions or delays.)*

---

## Likely questions (short answers)

- **Why not a neural network?** With 480 observations and a nearly linear relationship, even the random forest didn't
  help. More complexity would only add variance.
- **Why Ridge, if linear regression had lower error?** The gap (0.12 wins) is smaller than the between-season standard
  error (0.25). We picked the more stable model, using the one-standard-error rule.
- **What about injuries?** They're not in the model; that's the main limitation. Ratings come only from
  results, as if every team kept its early-season roster.
- **Why 15 games?** It's the fewest games any team has played today. The 0, 5 and 10-game versions show what happens
  before that.
- **Are the tiebreakers real?** No, they're random. The official NBA criteria are left for later.
- **Did you use AI?** Yes, Claude (Anthropic, Opus model), through Claude Code, to write and review code and text. The
  full statement is in the paper.
