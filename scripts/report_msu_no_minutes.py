import csv
p="data/processed/player_percentiles/player_percentiles_2026.csv"
with open(p,newline="") as f: rows=list(csv.DictReader(f))
players=[]
for r in rows:
 if "michigan state" in r["team_name"].lower() or (r["player_name"].lower()=="anton bonke" and "charlotte" in r["team_name"].lower()):
  old=float(r["spats_rating"]); mp=float(r["mpg_pctile"])
  new=(old-0.05*mp)/0.95
  players.append((r["team_name"],r["player_name"],new,old,mp))
for team,name,new,old,mp in sorted(players,key=lambda x:-x[2]):
 print(f"RATING|{team}|{name}|{new:.6f}|{old:.6f}|{mp:.6f}")
print("MSU_TOTAL",sum(p[2] for p in players if "michigan state" in p[0].lower()))
