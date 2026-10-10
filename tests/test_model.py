import pandas as pd
from src.model import calculate, retention

def test_weighted_ratings_and_team_shares():
    rows=[]
    for season in [2025,2026]:
        for team in ['A','B']:
            for i in range(3):
                rows.append(dict(season=season,team_id=team,player_id=f'{team}{i}',games=20,ppg=5+i,apg=1+i,ts_pct=45+i,orb_pg=1+i,drb_pg=2+i,spg=.5+i,bpg=.2+i,to_pg=2-i*.3,mpg=12+i*5))
    result=calculate(pd.DataFrame(rows))
    assert result.rating.between(0,100).all()
    assert all(abs(x-100)<1e-7 for x in result.groupby(['season','team_id']).team_value_pct.sum())
    assert not retention(result).empty
