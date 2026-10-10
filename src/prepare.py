"""Transform standardized player season totals into SPATS input fields."""
import numpy as np
import pandas as pd

def from_totals(df):
    required = ['season','team_id','player_id','games','minutes','pts','ast','orb','drb','stl','blk','tov','fga','fta']
    missing = set(required)-set(df.columns)
    if missing: raise ValueError(f'Missing raw totals: {sorted(missing)}')
    out = df[['season','team_id','player_id','games']].copy()
    g = df.games.replace(0,np.nan)
    for dest,src in [('ppg','pts'),('apg','ast'),('orb_pg','orb'),('drb_pg','drb'),('spg','stl'),('bpg','blk'),('to_pg','tov'),('mpg','minutes')]:
        out[dest] = df[src]/g
    denom = 2*(df.fga+0.44*df.fta)
    out['ts_pct'] = (100*df.pts/denom.replace(0,np.nan))
    return out
