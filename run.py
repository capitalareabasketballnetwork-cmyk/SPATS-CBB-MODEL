import sys
from pathlib import Path
import pandas as pd
from src.prepare import from_totals
from src.model import calculate, retention

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python run.py data/player_totals.csv")
    totals = pd.read_csv(sys.argv[1])
    ratings = calculate(from_totals(totals))
    Path("output").mkdir(exist_ok=True)
    ratings.to_csv("output/player_ratings.csv", index=False)
    retention(ratings).to_csv("output/team_retention.csv", index=False)
    print(f"Processed {len(ratings)} player seasons; {ratings.complete.sum()} complete")
