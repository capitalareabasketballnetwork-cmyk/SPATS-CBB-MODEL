import csv,json,urllib.request,collections
url="https://sports.core.api.espn.com/v2/sports/basketball/leagues/mens-college-basketball/seasons/2027/types/2/groups/50/teams?limit=500"
with urllib.request.urlopen(url,timeout=40) as f:d=json.load(f)
print("ROSTER_AUDIT",d.get("count"),len(d.get("items",[])))
for item in d.get("items",[])[:3]:
 print("TEAMREF",item.get("$ref"))
 try:
  u=item["$ref"].split("?")[0]+"/athletes?limit=50"
  with urllib.request.urlopen(u,timeout=25) as f:x=json.load(f)
  print("ATHLETES",x.get("count"),len(x.get("items",[])),str(x.get("items",[]))[:300])
 except Exception as e:print("ERR",str(e))
