"""Rank 2026-27 team rosters by prior-season Division I SPATS player ratings."""
import concurrent.futures,csv,json,pathlib,urllib.request,time
base="https://sports.core.api.espn.com/v2/sports/basketball/leagues/mens-college-basketball/seasons/2027"
headers={"User-Agent":"SPATS-CBB-Research/1.0"}
def get(url):
 with urllib.request.urlopen(urllib.request.Request(url.replace("http:","https:"),headers=headers),timeout=25) as f:return json.load(f)
with open("data/processed/d1_player_percentiles/player_percentiles_2026.csv",newline="") as f:old=list(csv.DictReader(f))
by_id={}
for r in old:
 if r["spats_rating"]:
  p=r["player_id"]
  if p not in by_id or float(r["games"])>float(by_id[p]["games"]):by_id[p]=r
d=get(base+"/types/2/groups/50/teams?limit=500")
teams=[x["$ref"].split("/teams/")[-1].split("?")[0] for x in d["items"]]
print("ROSTER_COUNT",len(teams),flush=True)
def one(team):
 try:
  d=get(base+"/teams/"+team+"/athletes?limit=60")
  ids=[a["$ref"].split("/athletes/")[-1].split("?")[0] for a in d.get("items",[])]
  matches=[by_id[p] for p in ids if p in by_id]
  return dict(team_id=team,players=len(ids),rated=len(matches),value=round(sum(float(r["spats_rating"]) for r in matches),4),names="; ".join(r["player_name"] for r in matches),ids=";".join(r["player_id"] for r in matches),error="")
 except Exception as e:return dict(team_id=team,players=0,rated=0,value=0,names="",ids="",error=str(e))
with concurrent.futures.ThreadPoolExecutor(max_workers=24) as pool:out=list(pool.map(one,teams))
errors=[r for r in out if r["error"]]
print("ROSTER_ERRORS",len(errors),errors[:5],flush=True)
if errors:raise RuntimeError("Cannot certify national rankings: missing rosters")
if sum(x["rated"] for x in out)<1500:raise RuntimeError("Insufficient rated player matches")
teamnames={r["team_id"]:r["team_name"] for r in old}
out.sort(key=lambda x:x["value"],reverse=True)
for i,r in enumerate(out[:30],1):
 print("ROSTER_TOP",i,teamnames.get(r["team_id"],r["team_id"]),r["value"],r["rated"],r["players"],r["names"],flush=True)
for r in out:
 if r["team_id"] in ("127","1270") or "Michigan State" in teamnames.get(r["team_id"],""):
  print("ROSTER_MSU",r,flush=True)
p=pathlib.Path("data/processed/2027_roster_spats_rankings.csv");p.parent.mkdir(exist_ok=True,parents=True)
with p.open("w",newline="") as f:
 w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
