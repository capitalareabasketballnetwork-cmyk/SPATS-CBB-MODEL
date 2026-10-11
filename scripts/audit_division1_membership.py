import json,urllib.request
base="https://sports.core.api.espn.com/v2/sports/basketball/leagues/mens-college-basketball/seasons"
for yr in (2005,2015,2025,2026):
 url=f"{base}/{yr}/types/2/groups/50/teams?limit=500"
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"SPATS/1.0"}),timeout=40) as f:d=json.load(f)
  ids=[str(t.get("$ref","")).split("/teams/")[-1].split("?")[0] for t in d.get("items",[])]
  print("COREAUDIT",yr,"count",d.get("count"),"items",len(ids),"ids",",".join(ids[:10]),"url",url)
 except Exception as e:print("COREERROR",yr,str(e))
