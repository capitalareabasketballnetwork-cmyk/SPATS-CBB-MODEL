# Cached historical SPATS player percentiles

The workflow [Build historical player percentiles](../../.github/workflows/build-player-percentiles.yml) generates one independent CSV per men's college basketball season from 2003 through 2026, inclusive. Files are committed here after a successful build.

- `player_percentiles_YYYY.csv`: one row per player/team/season, raw season totals, per-game stats, national midrank percentiles, SPATS rating, and team value share.
- `manifest.csv`: per-season row counts, team counts, missing ratings, and coverage warnings.
- Source: `hoopR::load_mbb_player_box(seasons=YYYY)`.
- A player appearing for two teams in the same season receives separate rows.
- Percentiles compare player-season averages with **players from the same season only**; the reference excludes players with fewer than five games.
- Percentile ties use midranks; turnovers per game are reverse-scored.
- Rating weights: PPG 25%, APG 15%, TS% 15%, ORB/G 8%, DRB/G 7%, STL/G 10%, BLK/G 5%, TOV/G 10% (reverse), MPG 5%.
- Team value is `rating * minutes per game * games` divided by the same quantity summed across that team's players. This is a heuristic, not measured wins added.
- If true shooting denominator is zero, TS% and rating are missing. Extremely small shooting samples can produce TS% above 100%; the formula is intentionally not capped.
- **2003 and 2004 are severely incomplete in the previously downloaded box-score data.** Their files are retained for transparency but must not be treated as representative national datasets.
- 2005–2026 have much more coverage, but season completeness and Division I membership still need independent auditing. Source includes whatever teams ESPN/hoopR returns; **the workflow does not yet filter against an independently verified Division I team-season membership list**. Accordingly these are source-wide season percentiles, not a certified D-I-only population.

Regenerate via GitHub Actions > Build historical player percentiles > Run workflow. The workflow writes generated CSVs back to the repository so subsequent queries do not need to recompute them.
