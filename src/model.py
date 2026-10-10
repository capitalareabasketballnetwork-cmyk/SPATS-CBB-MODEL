"""SPATS player ratings and within-team value shares.
Input: one row per player-season, with nationally comparable Division I data.
"""
import numpy as np
import pandas as pd

WEIGHTS = {'ppg':.25,'apg':.15,'ts_pct':.15,'orb_pg':.08,'drb_pg':.07,'spg':.10,'bpg':.05,'to_pg':.10,'mpg':.05}
REVERSE = {'to_pg'}

def calculate(df: pd.DataFrame, min_games: int = 5) -> pd.DataFrame:
    required = {'season','team_id','player_id','games'} | set(WEIGHTS)
    missing = required - set(df.columns)
    if missing: raise ValueError(f'Missing columns: {sorted(missing)}')
    out = df.copy()
    for season, group in out.groupby('season'):
        eligible = group[group.games >= min_games]
        for stat, weight in WEIGHTS.items():
            reference = pd.to_numeric(eligible[stat], errors='coerce').dropna()
            if len(reference) < 2:
                out.loc[group.index,stat+'_pctile'] = np.nan
                continue
            vals = pd.to_numeric(group[stat],errors='coerce')
            pct = vals.map(lambda v: (100 * ((reference < v).sum() + .5*(reference == v).sum()) / len(reference)) if pd.notna(v) else np.nan)
            if stat in REVERSE: pct = 100-pct
            out.loc[group.index,stat+'_pctile'] = pct
    columns = [k+'_pctile' for k in WEIGHTS]
    out['complete'] = out[columns].notna().all(axis=1)
    out['rating'] = sum(out[k+'_pctile']*w for k,w in WEIGHTS.items()).where(out.complete)
    out['value_units'] = out.rating * out.mpg.clip(lower=0) * out.games.clip(lower=0)
    total = out.groupby(['season','team_id']).value_units.transform('sum')
    out['team_value_pct'] = (100*out.value_units/total).where(total.gt(0))
    return out

def retention(ratings: pd.DataFrame) -> pd.DataFrame:
    """Value retained by same-school returners; transfers do not count as retained."""
    prior = ratings[['season','team_id','player_id','team_value_pct']].copy()
    nxt = ratings[['season','team_id','player_id']].drop_duplicates().copy()
    nxt['season'] -= 1
    matched = prior.merge(nxt.assign(returned=True),on=['season','team_id','player_id'],how='left')
    matched['retained'] = matched.team_value_pct.where(matched.returned.eq(True),0)
    result = matched.groupby(['season','team_id'],as_index=False).retained.sum()
    result['next_season'] = result.season+1
    return result.rename(columns={'retained':'returning_value_pct'})
