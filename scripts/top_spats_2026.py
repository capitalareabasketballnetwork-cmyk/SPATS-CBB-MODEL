import csv
rows=list(csv.DictReader(open("data/processed/player_percentiles/player_percentiles_2026.csv",newline="")))
rank=[]
for r in rows:
 try:
  score=(float(r["spats_rating"])-0.05*float(r["mpg_pctile"]))/0.95
  rank.append((score,r["player_name"],r["team_name"]))
 except (ValueError,KeyError): pass
for i,(score,name,team) in enumerate(sorted(rank,reverse=True)[:25],1):
 print("TOPPLAYER",i,name,team,round(score,3))
