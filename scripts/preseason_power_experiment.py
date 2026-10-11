import csv,json,urllib.request,pathlib
with open("data/processed/2027_team_talent_rankings.csv",newline="") as f:teams=list(csv.DictReader(f))
url="https://site.api.espn.com/apis/v2/sports/basketball/mens-college-basketball/standings?season=2026&group=50"
with urllib.request.urlopen(url,timeout=40) as f:stand=json.load(f)
records={}
for conf in stand.get("children",[]):
 for e in conf.get("standings",{}).get("entries",[]):
  tid=str(e.get("team",{}).get("id",""))
  stats=e.get("stats",[])
  d={x.get("name"):x.get("value") for x in stats}
  for x in stats:
   if x.get("name") in ("overall","winPercent","wins","losses","overallWins","overallLosses"):print("SAMPLESTAT",tid,x.get("name"),x.get("value"),x.get("displayValue"),flush=True) if tid=="127" else None
  wins=next((float(x["value"]) for x in stats if x.get("name")=="wins"),None)
  losses=next((float(x["value"]) for x in stats if x.get("name")=="losses"),None)
  if wins is not None and losses is not None and wins+losses>0:records[tid]=wins/(wins+losses)
print("RECORDS",len(records),flush=True)
if len(records)<300:raise RuntimeError("Insufficient win-loss data; inspect stat fields")
out=[]
for t in teams:
 tid=t["team_id"]
 if tid not in records:continue
 talent=float(t["combined"])
 winpct=100*records[tid]
 score=.75*talent+.25*winpct
 out.append({"team":t["team"],"team_id":tid,"talent":round(talent,3),"win_pct":round(winpct,2),"power":round(score,3),"rated":t["rated"]})
out.sort(key=lambda x:x["power"],reverse=True)
print("POWER_COUNT",len(out),flush=True)
for i,r in enumerate(out[:35],1):print("POWER_RANK",i,r["team"],r["power"],r["talent"],r["win_pct"],flush=True)
for r in out:
 if r["team_id"]=="127":print("POWER_MSU",r,flush=True)
path=pathlib.Path("data/processed/2027_preseason_power_experiment.csv")
with path.open("w",newline="") as f:
 w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
