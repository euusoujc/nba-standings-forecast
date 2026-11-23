# Explanation guide — terms, metrics and what each number means

This guide follows the 14 slides of `apresentacao_en.html`, in the same order. The talk script (`roteiro_en.md`) says
**what to say** in 5 minutes; this guide explains **what everything means**, so you know the material and can answer
questions. All numbers are from the November 22, 2026 snapshot (N = 15 games).

For each term: **what it is** → **value in the project** → **what that implies**.

---

## Slide 1 — Title

**"15 games are not a season."** An NBA regular season has 82 games per team. After 15, each team has played less
than 20% of it. The title sums up the thesis: 15 games tell you a lot, but November standings should not be taken at
face value.

**Ridge and Monte Carlo** are the two parts of the method: Ridge estimates each team's strength; Monte Carlo turns
that strength into standings odds. Both are explained on slides 5, 8 and 9.

---

## Slide 2 — The question

**Win percentage** (*win %*): wins divided by games. Philadelphia at 14-3 is 14/17 = .824.

**Top 6 / play-in / out.** Each conference (East and West) has 15 teams.
- **Top 6** (1st to 6th): direct playoff berth.
- **Play-in** (7th to 10th): a mini tournament that decides the last two spots.
- **Out** (11th to 15th): eliminated.

**P(top 6)** is the probability that a team finishes in the top six. That, along with expected wins, is what the
project delivers.

---

## Slide 3 — Data

**nba_api**: a Python library that downloads data from the NBA's official stats site (`stats.nba.com`).

**Game log**: one row per team per game, with date, opponent, home/away, result, points and shooting stats.

**16 seasons, 480 team-seasons.** From 2010-11 to 2025-26 there are 16 seasons with 30 teams: 16 × 30 = 480. Each
team in each season is **one observation**. That is small for machine learning (which is why simple models do well
here, see slide 7).

**Features** (input variables), all computed **from the first 15 games only**:

| Feature | What it is | Example (PHI) |
|---|---|---|
| Win % | wins / games | 12-3 in the first 15 = .800 |
| Point diff per game | (points scored − allowed) / games | +2.8 |
| Net rating | point differential per 100 possessions (adjusts for pace) | +2.7 |
| Pythagorean | win % "earned" by points scored and allowed (slide 5) | .586 |
| Strength of schedule | average win % of the opponents faced | .460 |
| Last season | previous season's final win % | .549 |

**Target**: what the model tries to predict. Here it is the **final win %**, not wins, because 2011-12, 2019-20 and
2020-21 had fewer than 82 games. Errors are converted to wins by multiplying by 82.

**Leakage** (*data leakage*): accidentally using information that would not exist at prediction time. Example:
computing strength of schedule with December games to predict in November. We avoid it by cutting everything at each
team's 15th game.

---

## Slide 4 — Regression to the mean

**Regression to the mean**: when a measurement is noisy, extreme values tend to come back toward the average the next
time. A team that starts 12-3 probably had some luck; one that starts 3-12, some bad luck.

**The chart**: each dot is a team-season. x axis = win % after 15 games; y axis = final win %.
- The **dashed line** (y = x) is what would happen if the start were the truth.
- The **red line** is the fitted line: **final = 0.18 + 0.63 × win % after 15 games**.

**Slope 0.63** → every point above .500 early on is worth only 63% by the end. Example: a team at .800 after 15 games
(30 points above .500) finishes, on average, around .500 + 0.63 × 0.300 ≈ **.69**.

**Why does the line cross .500?** Because 0.18 + 0.63 × 0.5 ≈ 0.50: an average team early on stays average.

**Standard deviation** drops from 0.190 (after 15 games) to 0.151 (end of season): early records are more spread out
because they carry more noise.

**What it implies:** any good forecast has to "shrink" early records toward .500. That is what the models learn, and
what the naive baseline does not do.

---

## Slide 5 — The models

**Baseline**: a very simple reference model that serves as a yardstick. If a fancy model can't beat the baseline, it
isn't worth using.

- **Keep win %**: assumes each team finishes with today's win %. PHI would end up with .800 × 82 ≈ 66 wins.
- **Pythagorean** (Pythagorean expectation): estimates win % from points, PF¹⁴ / (PF¹⁴ + PA¹⁴), where PF is points
  for and PA points against. The exponent 14 is the usual value for basketball. The idea: the scoreboard says more
  about strength than close wins and losses. PHI's is .586, well below its .800 record.

**Linear regression (OLS, ordinary least squares)**: finds the combination of the six features
(ŷ = β₀ + β₁x₁ + … + β₆x₆) that minimizes the sum of squared errors. The **β coefficients** say how much each feature
weighs.

**Standardized features**: each feature is rescaled to mean 0 and standard deviation 1 before training. That makes
coefficients comparable (point differential in points and win % as a fraction end up on the same scale).

**Ridge** (L2-penalized regression): linear regression with a penalty on large coefficients. It minimizes

> sum of squared errors + **α** × sum of squared coefficients

- **α (alpha)** sets the strength of the penalty. α = 0 is OLS; a large α pushes every coefficient toward zero.
- In this project, **α = 100**.
- In practice: when two features say the same thing, Ridge **splits the weight** between them instead of giving one a
  huge positive coefficient and the other a huge negative one (slide 8).

**Lasso** (L1 penalty): penalizes the sum of the **absolute values** of the coefficients. Unlike Ridge, it can set
coefficients to exactly zero, so it does feature selection.

**Random forest**: the average of 500 decision trees, each trained on a different sample of the data. It captures
nonlinear relationships. **Min leaf 10** = each leaf of a tree must hold at least 10 teams, so the trees don't
memorize the data.

---

## Slide 6 — Validation

**Validation**: measuring error on data the model **did not see in training**. Measuring on the training data is
misleading, because the model may have memorized it.

**Leave-one-season-out (LOSO)**: hold out a whole season, train on the other 15 and predict the one left out. Repeat
16 times, once per season. Why by season and not by team? Teams in the same season share the same conditions (rules,
pace, the 2020 bubble). Mixing them would be a form of leakage.

**Temporal holdout**: train on 2010-11 to 2022-23 and test on 2023-24 to 2025-26. It answers: does the model still
work in recent years?

**Nested α search** (*nested cross-validation*): Ridge's α is chosen with a validation run **inside** each training
set, also split by season. That way the test season never influences the choice of α.

**One-standard-error rule**: among all α values whose error is within one standard error of the best, pick the
**largest** (the simplest, most stable model). The logic: if two models are statistically tied, keep the more
conservative one.

**Standard error**: how much an average moves from sample to sample. Here, how much the model's error changes from one
season to another.

**The two metrics** are on slide 7.

---

## Slide 7 — Results

**MAE** (*mean absolute error*): the average of |actual − predicted|, converted to wins on an 82-game scale. It is the
main metric.

| Model | MAE (LOSO) | What it means |
|---|---|---|
| Baseline "keep win %" | **7.60** | misses by 7.6 wins per team on average |
| Ridge | **5.62** | misses by 5.6 wins per team |
| OLS / Lasso / Random forest | 5.50 / 5.68 / 5.72 | essentially the same as Ridge |
| Temporal holdout 2023-26 (Ridge) | **5.35** | in recent years it does slightly better |

**What it implies:** the models take **two wins** off the error. Two wins often separate 6th from 7th place.

**Spearman** (rank correlation): measures whether the predicted **order** matches the actual order, from −1 (reversed)
to +1 (perfect). Computed per conference and season, then averaged.
- Ridge: **0.78**; baseline: 0.74.
- 0.78 means the predicted standings get the order mostly right, but not perfectly: swaps between neighbors are common.

**"Tied within one standard error (0.25 wins)"**: MAE moves by 0.25 wins from season to season just by chance. Since
OLS, Ridge, Lasso and random forest differ by less than that, **you can't say one is better**. The slide's takeaway:
the gain comes from shrinking the start, not from the choice of algorithm.

---

## Slide 8 — Why Ridge

**Correlation** (Pearson): measures whether two variables move together, from −1 to +1. Point diff per game and net
rating correlate at **0.999**: they are practically the same information, except net rating adjusts for pace.

**Multicollinearity**: when features are near copies of each other. OLS becomes unstable: any combination of weights
that adds up to the same result fits equally well.

**The chart** (standardized coefficients):

| Feature | OLS | Ridge |
|---|---|---|
| Point diff per game | **+0.161** | +0.023 |
| Net rating | **−0.180** | +0.023 |
| Pythagorean | +0.075 | +0.024 |
| Win % | +0.053 | +0.036 |
| Last season | +0.032 | +0.028 |
| Strength of schedule | +0.007 | +0.007 |

- In OLS, net rating gets a **negative** weight: it would say a team that outscores opponents more per possession is
  worse. That makes no sense; it's OLS offsetting one coefficient with the other.
- Ridge splits the weight evenly across the three point-based features.
- Strength of schedule barely matters: after 15 games, opponents' records are noisy too.

**What it implies:** same error as OLS, but with coefficients you can interpret and that don't swing much if the data
change a little. That is why we chose Ridge.

---

## Slide 9 — Simulation

**Rating**: each team's strength = the final win % that Ridge predicts. Examples (from the first 15 games):

| Team | Record in first 15 | Point diff/game | Rating (Ridge) |
|---|---|---|---|
| San Antonio | 12-3 | +11.2 | .727 (≈ 60 wins) |
| Boston | 11-4 | +10.5 | .693 (≈ 57) |
| Philadelphia | 12-3 | +2.8 | .592 (≈ 49) |

Philadelphia and San Antonio have the same record, but PHI's point differential is much smaller. The model trusts
point differential more.

**σ (sigma) = 0.085**: rating uncertainty. In each simulation, every rating gets random noise with this standard
deviation. 0.085 × 82 ≈ **7 wins**: a team's true strength can typically sit 7 wins above or below its rating.
Without this noise, the simulation would think it knows each team's strength exactly, and the intervals would be too
narrow.

**Logistic regression (game model)**: turns the strength gap into a win probability for one game:

> logit P(win) = 4.35 × (team rating − opponent rating) + 0.32 × home

- **logit** is the scale logistic regression works on: logit(p) = ln(p / (1 − p)). Convert back with
  p = 1 / (1 + e^(−logit)).
- **Home** = +1 at home, −1 away.
- **Between equal teams, the home team wins 57.9%**: that's the 0.32 term. It is home-court advantage.
- Example: a rating 0.10 higher (≈ 8 wins over a season) on a neutral court → 4.35 × 0.10 = 0.435 → **60.7%** chance;
  at home → **68%**.
- Accuracy of 64.3% on historical games: it picks the winner in almost 2 of every 3 games. Basketball has a lot of
  game-to-game randomness, so that is a normal value.

**Monte Carlo**: instead of computing probabilities with a formula, play out the whole season many times. Each of the
**10,000 simulations** draws the **952 remaining games** using the game model's odds, adds them to current wins and
builds the standings. A team's P(top 6) is the share of the 10,000 simulations in which it finished in the top six.

**2 NBA Cup games**: scheduled games add up to 80 per team; the other 2 depend on the NBA Cup knockout stage and have
no opponent yet. We simulate them against an average opponent on a neutral court.

**Outputs**:
- **Expected wins**: the average wins across the 10,000 simulations.
- **80% interval** (80% CI): from the 10th to the 90th percentile of simulated wins. Philadelphia: 44 to 60 wins. That
  is: in 80% of simulations, PHI finishes in that range.
- **P(top 6), P(play-in), P(out)**: they add up to 100% for each team.

---

## Slide 10 — Backtest

**Backtest**: testing the method on the past, as if we were living in that moment. For each of the 16 seasons, we go
back to the day the last team completed 15 games and simulate the rest, **without using that season in training**
(rating, game model and σ refitted without it). Then we compare with what actually happened.

**Coverage of the 80% interval = 81%**: the 80% interval contained the actual wins in 81% of the 480 team-seasons.
- At 60%, the intervals would be too narrow (an overconfident model).
- At 95%, they would be too wide (an underconfident model).
- 81% close to 80% means **the uncertainty is measured well**.

**Brier score** (3 classes): measures the error of probabilities. For each team, add up (predicted probability −
outcome)² over the three classes (top 6, play-in, out), where the outcome is 1 if it happened and 0 if not. It ranges
from 0 (perfect) to 2 (worst possible). **Lower is better.**
- Example: the model gave 90% top 6, 9% play-in and 1% out, and the team finished top 6:
  (0.90 − 1)² + (0.09 − 0)² + (0.01 − 0)² = 0.018. Great.
- **Simulation: 0.42.**
- **Reference: 0.66**, the Brier score of always guessing the fixed shares 6/15, 4/15 and 5/15 for every team.
- **What it implies:** the model's probabilities are much better than knowing nothing.

**Calibration** (the chart in the paper): when the model says 30%, the event happens about 30% of the time. "When it
says 80%, it hits 81%" sums that up.

---

## Slide 11 — Versions V0, V5, V10, V15

**What they are**: the whole pipeline rerun on four dates of the 2026-27 season, each with what was known that day.

| Version | Date | What the model uses | Backtest Brier | Error on final wins | 80% coverage |
|---|---|---|---|---|---|
| V0 | Oct 19 (eve of opening night) | last season only | 0.533 | 7.8 | 87% |
| V5 | Nov 2 | first 5 games | 0.488 | 7.0 | 81% |
| V10 | Nov 11 | first 10 games | 0.444 | 6.0 | 79% |
| V15 | Nov 22 | first 15 games | 0.421 | 5.3 | 81% |

**"Error on final wins"** here is the backtest MAE: the average gap between the simulation's expected wins and actual
wins. It is a bit lower than the 5.6 on slide 7 because the simulation already counts the wins a team has banked.

**What it implies:**
- Every block of 5 games improves the forecast, and the gain is biggest early on.
- At V0 coverage is 87%: the intervals are a bit wide, because the model knows little.
- From V5 on, the uncertainty is already well measured (coverage near 80%).

**Teams that changed tier**: Memphis came off a 25-win season and started 11-4 with a strong point differential; it
went from 33 to 48 expected wins (P(top 6) from 14% to 48%). Toronto rose to 49 at V5 and fell to 38 at V15: a good
start that didn't last. That is why one snapshot isn't enough.

---

## Slide 12 — 2026-27 projection

**Heatmap**: each row is a team, each column a final position (1 to 15), and each number is the % of simulations in
which the team finished in that position. The solid red line marks the top-six cutoff; the dashed one, the play-in
cutoff.

| Team | Record | Expected wins | 80% CI | P(top 6) | P(play-in) | P(out) |
|---|---|---|---|---|---|---|
| Boston | 11-6 | 55.8 | 48–63 | 97% | 3% | 0% |
| San Antonio | 14-3 | 58.9 | 51–66 | 95% | 5% | 0% |
| Philadelphia | 14-3 | 52.4 | 44–60 | 90% | 9% | 0% |
| Memphis | 12-5 | 48.5 | 40–57 | 48% | 46% | 6% |

**How to read Philadelphia**: if kept up, the 14-3 record would project to about 67 wins. The model projects 52.4
because a +2.8 point differential per game looks like a good team, not a title contender. The 14 wins already banked
count; what the model shrinks is the pace from here on.

**Boston has a worse record than PHI but better odds**: +10.5 point differential per game and a strong previous
season (.683). The model reads Boston as stronger than its record shows.

---

## Slide 13 — Lessons

- **Validating by season, no leakage**: the reason the numbers can be trusted.
- **A simple linear model tied the forest**: with 480 observations and a nearly linear relationship (slide 4), a
  complex model has nothing extra to learn.
- **Testing the simulation on the past**: the backtest (slide 10) is what shows the probabilities make sense.
- **With 5 games the error already drops from 13.3 to 7.2**: from the sensitivity analysis. After 5 games, keeping the
  current win % misses by 13.3 wins (the start is pure noise); Ridge misses by 7.2, almost half. The model is most
  useful exactly when there is least information.

**Next time**:
- **Injuries, trades and roster changes**: the model assumes each team keeps its early-season roster. A starter out
  for a month moves things more than the average error.
- **20, 25, 30-game versions**: keep following the season.
- **Ratings updated after every game**: today the rating uses only each team's first 15 games.
- **Official tiebreakers**: today ties in the standings are broken at random.

---

## Slide 14 — Takeaway

**"Trust the record, but shrink it first"**: the record carries information, but it has to be pulled toward the mean
and combined with point differential and last season.

**Living project**: the data come straight from the NBA's API. Running `python src/coleta.py --refresh-current` and the
notebook again recomputes everything with the latest games.

**AI use**: code and text built with help from Claude (Anthropic, Opus model), through Claude Code. The full statement
is at the end of the paper.

---

## Quick glossary

| Term | In one sentence | Value in the project |
|---|---|---|
| 80% interval (80% CI) | range between the 10th and 90th percentiles of the simulations | PHI 44–60 |
| α (alpha) | strength of Ridge's penalty | 100 |
| Backtest | testing the method on the past without using that year in training | 16 seasons |
| Baseline | simple model used as a yardstick | MAE 7.60 |
| Brier score | error of the probabilities (0 = perfect; lower is better) | 0.42 (reference 0.66) |
| Calibration | the model saying 30% and it happening ~30% of the time | 81% coverage for 80% |
| Coefficient | weight of each feature in the linear model | Ridge ≈ 0.023 on point-based ones |
| Coverage | % of times the actual result fell inside the interval | 81% |
| Feature | input variable of the model | 6 |
| Lasso | regression with an L1 penalty, can zero out coefficients | MAE 5.68 |
| Leakage | accidentally using information from the future | cut at the 15th game |
| Logistic regression | turns a strength gap into a probability | home team 57.9% between equals |
| Logit | log-odds scale of logistic regression, ln(p/(1−p)) | b_diff 4.35; b_home 0.32 |
| LOSO | leave one season out at a time | 16 rounds |
| MAE | mean absolute error, in wins | Ridge 5.62 |
| Monte Carlo | play out the season many times and count the results | 10,000 simulations |
| Multicollinearity | features that are nearly identical | point diff × net rating: 0.999 |
| Net rating | point differential per 100 possessions | PHI +2.7 |
| OLS | linear regression by least squares | MAE 5.50 |
| One-standard-error rule | among tied models, keep the simplest | picked α = 100 |
| Pythagorean | win % "earned" by points, PF¹⁴/(PF¹⁴+PA¹⁴) | MAE 6.83 as a baseline |
| Random forest | average of many decision trees | MAE 5.72 |
| Rating | a team's predicted strength (Ridge final win %) | SAS .727 |
| Regression to the mean | extreme starts drift back toward the average | slope 0.63 |
| Ridge | linear regression with an L2 penalty | the chosen model |
| σ (sigma) | rating uncertainty | 0.085 (≈ 7 wins) |
| Spearman | whether the predicted order matches the actual one (−1 to 1) | 0.78 |
| Standard error | how much an average moves by chance | 0.25 wins |
| Temporal holdout | train on the past, test on recent years | MAE 5.35 |
| Win % | wins / games | PHI 14-3 = .824 |
