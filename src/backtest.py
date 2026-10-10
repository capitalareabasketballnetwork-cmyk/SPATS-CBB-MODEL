"""Out-of-sample season-forward backtesting. Inputs must be prepared separately."""
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score

def evaluate(feature_table: pd.DataFrame, start_test_season: int = 2006):
    """Expected: season=target season, returning_value_pct, prior_win_pct, target_win_pct.
    Train only on target seasons strictly before test season; report annual errors.
    """
    features=['returning_value_pct','prior_win_pct']
    df=feature_table.dropna(subset=features+['target_win_pct']).copy()
    rows=[]
    for year in sorted(df.season.unique()):
        if year < start_test_season: continue
        train=df[df.season < year]
        test=df[df.season == year]
        if len(train)<30 or test.empty: continue
        model=Ridge(alpha=1.0).fit(train[features],train.target_win_pct)
        prediction=model.predict(test[features]).clip(0,1)
        rows.append({'season':int(year),'n_teams':len(test),'mae_win_pct':mean_absolute_error(test.target_win_pct,prediction),'r2':r2_score(test.target_win_pct,prediction) if len(test)>1 else float('nan')})
    return pd.DataFrame(rows)
