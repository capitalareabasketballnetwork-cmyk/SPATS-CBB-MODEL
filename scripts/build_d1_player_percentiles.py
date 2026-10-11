"""Rebuild SPATS ratings using season-specific NCAA D-I team IDs only."""
import bisect,csv,json,math,pathlib,urllib.request,sys
src=pathlib.Path("data/processed/player_percentiles")
dest=pathlib.Path("data/processed/d1_player_percentiles")
dest.mkdir(parents=True,exist_ok=True)
weights={"ppg":.25,"apg":.15,"ts_pct":.15,"orb_pg":.08,"drb_pg":.07,"spg":.10,"bpg":.05,"to_pg":.10}
base="https://sports.core.api.espn.com/v2/sports/basketball/leagues/mens-college-basketball/seasons"
def fetch_ids(yr):
 url=f"{base}/{yr}/types/2/groups/50/teams?limit=500"
 with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"SPATS-CBB/1.0"}),timeout=45) as f:d=json.load(f)
 refs=[t.get("$ref","") for t in d.get("items",[])]
 ids={x.split("/teams/")[-1].split("?")[0] for x in refs if "/teams/" in x}
 if not (250<=len(ids)<=400) or d.get("count",0)>len(ids):
  raise RuntimeError(f"Unverified D-I membership for {yr}: {len(ids)} teams; API count {d.get('count')}")
 return ids
def val(row,key):
 try:
  n=float(row[key])
  return n if math.isfinite(n) else None
 except (ValueError,KeyError,TypeError):return None
def process(yr):
 ids=fetch_ids(yr)
 with (src/f"player_percentiles_{yr}.csv").open(newline="") as f:rows=list(csv.DictReader(f))
 excluded={r["team_name"] for r in rows if r["team_id"] not in ids}
 rows=[r for r in rows if r["team_id"] in ids]
 if not rows:raise RuntimeError("No D-I player rows")
 for k in weights:
  ref=sorted(v for r in rows if val(r,"games") is not None and val(r,"games")>=5 if (v:=val(r,k)) is not None)
  if len(ref)<2:raise RuntimeError(f"No valid reference for {yr} {k}")
  for r in rows:
   v=val(r,k)
   pct=None if v is None else 100*(bisect.bisect_left(ref,v)+bisect.bisect_right(ref,v))/(2*len(ref))
   if pct is not None and k=="to_pg":pct=100-pct
   r[k+"_pctile"]="" if pct is None else f"{pct:.10f}"
 for r in rows:
  scores=[val(r,k+"_pctile") for k in weights]
  rating=None if any(v is None for v in scores) else sum(weights[k]*val(r,k+"_pctile") for k in weights)/.95
  r["spats_rating"]="" if rating is None else f"{rating:.8f}"
  r["value_units"]=r["spats_rating"]
  r["mpg_pctile"]="" # no minutes in rating
 totals={}
 for r in rows:
  if r["spats_rating"]:totals[r["team_id"]]=totals.get(r["team_id"],0)+float(r["spats_rating"])
 for r in rows:
  r["team_value_pct"]=f"{100*float(r['spats_rating'])/totals[r['team_id']]:.8f}" if r["spats_rating"] and totals.get(r["team_id"]) else ""
 rows.sort(key=lambda r:(r["team_name"],-float(r["spats_rating"] or 0),r["player_name"]))
 out=dest/f"player_percentiles_{yr}.csv"
 with out.open("w",newline="") as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 print("D1_SEASON",yr,"teams",len({r["team_id"] for r in rows}),"members",len(ids),"players",len(rows),"excluded_teams",len(excluded))
 if yr==2026:
  for i,r in enumerate(sorted((r for r in rows if r["spats_rating"]),key=lambda r:float(r["spats_rating"]),reverse=True)[:25],1):
   print("D1_TOP",i,r["player_name"],r["team_name"],r["spats_rating"])
  for r in rows:
   if r["team_name"]=="Michigan State Spartans" or "bonke" in r["player_name"].lower():
    print("D1_MSU",r["player_name"],r["team_name"],r["spats_rating"])
 return dict(season=yr,division1_teams=len(ids),teams_with_player_data=len({r["team_id"] for r in rows}),players=len(rows),excluded_teams=len(excluded))
years=[int(x) for x in sys.argv[1:]] or list(range(2003,2027))
results=[process(y) for y in years]
with (dest/"manifest.csv").open("w",newline="") as f:
 w=csv.DictWriter(f,fieldnames=list(results[0]));w.writeheader();w.writerows(results)
