import csv,pathlib
p=pathlib.Path("data/processed/2027_roster_spats_rankings.csv")
with p.open(newline="") as f: rosters=list(csv.DictReader(f))
with open("data/processed/d1_player_percentiles/player_percentiles_2026.csv",newline="") as f: old=list(csv.DictReader(f))
ratings={r["player_id"]:float(r["spats_rating"]) for r in old if r["spats_rating"]}
names={r["team_id"]:r["team_name"] for r in old}
results=[]
for row in rosters:
 vals=sorted((ratings[x] for x in row["ids"].split(";") if x in ratings),reverse=True)
 if len(vals)<8:continue
 five=sum(vals[:5])/5
 eight=sum(vals[:8])/8
 combined=.6*five+.4*eight
 results.append(dict(team=names.get(row["team_id"],row["team_id"]),team_id=row["team_id"],rated=len(vals),top5=round(five,4),top8=round(eight,4),combined=round(combined,4),top8_players="; ".join(str(round(x,2)) for x in vals[:8])))
print("QUALIFYING",len(results),flush=True)
for metric in ["top5","top8","combined"]:
 print("LEADERBOARD",metric,flush=True)
 for i,r in enumerate(sorted(results,key=lambda x:x[metric],reverse=True)[:25],1):print("RANK",metric,i,r["team"],r["top5"],r["top8"],r["combined"],r["rated"],flush=True)
for r in results:
 if r["team_id"]=="127":print("MSU",r,flush=True)
path=pathlib.Path("data/processed/2027_team_talent_rankings.csv")
with path.open("w",newline="") as f:
 w=csv.DictWriter(f,fieldnames=list(results[0]));w.writeheader();w.writerows(sorted(results,key=lambda x:x["combined"],reverse=True))
