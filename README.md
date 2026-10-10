# SPATS College Basketball Model

**Status: reproducible modeling scaffold; historical datasets have NOT yet been downloaded or validated.**

Scope: NCAA Division I men's basketball, target seasons ending **2000–2026** (1999–2000 through 2025–26). Future 2026–27 ratings will use 2025–26 data and verified 2026–27 rosters.

## Model

National player rating = sum of national within-season percentile × weight. Points/game 25%, assists/game 15%, true shooting 15%, offensive rebounds/game 8%, defensive rebounds/game 7%, steals/game 10%, blocks/game 5%, **turnovers/game 10% (reverse-ranked)**, minutes/game 5%. Percentiles are computed against qualifying D-I players, with a minimum-games threshold (default 5). All nine statistics must be available for a complete rating; missing values are never silently filled with zero.

**Team value %** = `100 × (player rating × minutes/game × games) / sum(team players' rating × minutes/game × games)`. This is a transparent *allocation heuristic*, **not a causal estimate of wins contributed**. It uses minutes twice (once in the rating and again in the share), an explicit assumption to test in sensitivity analyses. Team shares sum to 100% among fully scored players. Incomplete player data can invalidate the shares; require full roster coverage before publishing them.

**Returning value %** = sum of prior-year team value shares for players who remain at the **same school** the next season. Transfers count as departures from their prior team and can be evaluated separately as additions at their destination. Match stable player IDs, not names alone.

## Data requirements

Required raw CSV columns: `season,team_id,player_id,games,minutes,pts,ast,orb,drb,stl,blk,tov,fga,fta`. Season is the ending calendar year (2026 = 2025–26). Include every D-I player-season, not only Michigan State.

Data sourcing: [Sports Reference college basketball](https://www.sports-reference.com/cbb/) reports most stats since 1999–2000, subject to coverage and licensing. [SportsDataverse hoopR](https://hoopr.sportsdataverse.org/) offers player box-score data beginning 2002–03. Confirm data rights, coverage, completeness and season-specific team membership before ingestion. Do not represent 2000–02 as complete until verified.

## Run locally

```bash
python -m pip install -r requirements.txt
python run.py data/player_totals.csv
```

Produces `output/player_ratings.csv` and `output/team_retention.csv`. `src/backtest.py` provides expanding-window testing after assembling historical outcomes and features. Do not fit percentiles on future seasons or use next-season roster information unavailable at the prediction date.

## Next development tasks

1. Implement and validate historical source-specific ingestion, data rights and coverage reports, 2000–2026.
2. Validate athlete IDs across transfers and seasons, D-I membership, minutes and full roster completeness.
3. Assemble team-season results (wins, games, strength of schedule) and prediction-date rosters.
4. Build season-forward features and run leakage-free out-of-sample backtests against a baseline using previous-season win% only.
5. Compare team-value allocation variants and sensitivity to minimum games, turnover reverse ranking, minutes, and missing data.
6. Publish Michigan State 2025–26 player ratings only after full national percentiles and roster checks.
