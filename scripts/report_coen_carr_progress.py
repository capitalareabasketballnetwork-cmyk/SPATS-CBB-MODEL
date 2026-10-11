import csv
for yr in (2024,2025,2026):
 path=f"data/processed/d1_player_percentiles/player_percentiles_{yr}.csv"
 with open(path,newline="") as f: rows=list(csv.DictReader(f))
 for r in rows:
  if "coen carr" in r["player_name"].lower():
   print("CARR_STATS",yr,{k:r.get(k) for k in ("games","ppg","apg","orb_pg","drb_pg","spg","bpg","to_pg","mpg","ts_pct","spats_rating")},flush=True)
