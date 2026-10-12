import csv,collections,json,urllib.request,statistics,math,pathlib
YEARS=range(2018,2027)
players={}
for y in range(2017,2027):
 with open(f"data/processed/d1_player_percentiles/player_percentiles_{y}.csv",newline="") as f: rows=list(csv.DictReader(f))
 by=collections.defaultdict(list)
 for r in rows:
  if r.get("spats_rating") and r.get("player_id") and r.get("team_id"):
   by[r["team_id"]].append({"id":r["player_id"],"rating":float(r["spats_rating"]),"name":r["player_name"],"team":r["team_name"],"games":float(r.get("games") or 0)})
 players[y]=by
 print("SEASON_ROWS",y,sum(map(len,by.values())),len(by),flush=True)
records={}
for y in range(2017,2027):
 url=f"https://site.api.espn.com/apis/v2/sports/basketball/mens-college-basketball/standings?season={y}&group=50"
 with urllib.request.urlopen(url,timeout=40) as f:d=json.load(f)
 rec={}
 for conf in d.get("children",[]):
  for e in conf.get("standings",{}).get("entries",[]):
   vals={x.get("name"):x.get("value") for x in e.get("stats",[])}
   w,l=vals.get("wins"),vals.get("losses")
   if w is not None and l is not None and float(w)+float(l)>0:
    rec[str(e["team"]["id"])]=float(w)/(float(w)+float(l))
 records[y]=rec
 print("RECORDS",y,len(rec),flush=True)
out=[]
for y in YEARS:
 prior={p["id"]:(team,p) for team,ps in players[y-1].items() for p in ps}
 seen={p["id"] for z in range(2017,y) for ps in players[z].values() for p in ps}
 for team,ps in players[y].items():
  if team not in records[y] or team not in records[y-1]:continue
  ret=[prior[p["id"]][1] for p in ps if p["id"] in prior and prior[p["id"]][0]==team]
  trans=[prior[p["id"]][1] for p in ps if p["id"] in prior and prior[p["id"]][0]!=team]
  unknown=[p for p in ps if p["id"] not in seen]
  if len(ps)<8:continue
  ret_top=sum(p["rating"]>=65 for p in ret)
  trans_top=sum(p["rating"]>=65 for p in trans)
  ret_high=sum(p["rating"]>=75 for p in ret)
  trans_high=sum(p["rating"]>=75 for p in trans)
  out.append(dict(year=y,team_id=team,team=ps[0]["team"],win_pct=records[y][team],prior_win_pct=records[y-1][team],win_change=records[y][team]-records[y-1][team],return_count=len(ret),return_stars=ret_top,return_elite=ret_high,return_rating_sum=round(sum(p["rating"] for p in ret),2),transfer_count=len(trans),transfer_stars=trans_top,transfer_elite=trans_high,transfer_rating_sum=round(sum(p["rating"] for p in trans),2),first_seen_count=len(unknown),rated_count=len(ps)))
print("SAMPLE",len(out),flush=True)
def mean(v):return round(statistics.mean(v)*100,2) if v else None
def corr(a,b):
 ma=statistics.mean(a);mb=statistics.mean(b)
 num=sum((x-ma)*(y-mb) for x,y in zip(a,b))
 den=math.sqrt(sum((x-ma)**2 for x in a)*sum((y-mb)**2 for y in b))
 return round(num/den,4) if den else None
for key in ["return_stars","return_elite","return_rating_sum","transfer_count","transfer_stars","transfer_rating_sum","first_seen_count"]:
 for outcome in ["win_pct","win_change"]:
  print("CORRELATION",key,outcome,corr([float(r[key]) for r in out],[r[outcome] for r in out]),flush=True)
 for label,pred in [("0",lambda n:n==0),("1",lambda n:n==1),("2",lambda n:n==2),("3plus",lambda n:n>=3)]:
  v=[r for r in out if pred(r[key])]
  if len(v)>=20:print("GROUP",key,label,len(v),mean([r["win_pct"] for r in v]),mean([r["win_change"] for r in v]),flush=True)
for y in [2023,2024,2025,2026]:
 v=[r for r in out if r["year"]==y]
 print("YEAR",y,len(v),flush=True)
 for key in ["return_stars","transfer_stars","first_seen_count"]:
  hi=[r for r in v if r[key]>=3];lo=[r for r in v if r[key]==0]
  print("YEAR_GROUP",y,key,"3plus",len(hi),mean([r["win_pct"] for r in hi]),"zero",len(lo),mean([r["win_pct"] for r in lo]),flush=True)
path=pathlib.Path("data/processed/historical_roster_patterns_2018_2026.csv")
with path.open("w",newline="") as f:
 w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
