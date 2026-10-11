import csv
p="data/processed/player_percentiles/player_percentiles_2026.csv"
with open(p,newline="") as f: rows=list(csv.DictReader(f))
for r in rows:
 if "bonke" in r["player_name"].lower() or "michigan state" in r["team_name"].lower():
  print("PLAYER_VALUE",r["team_name"],r["player_name"],"rating",r["spats_rating"],"team_pct",r["team_value_pct"],"units",r["value_units"])
