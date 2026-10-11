import json,urllib.request
urls=["https://site.api.espn.com/apis/v2/sports/basketball/mens-college-basketball/standings?season=2026&group=50","https://site.web.api.espn.com/apis/v2/sports/basketball/mens-college-basketball/standings?season=2026&group=50","https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/teams/127/record?season=2026"]
for u in urls:
 try:
  with urllib.request.urlopen(u,timeout=12) as f:d=json.load(f)
  print("TEST",u,"keys",list(d)[:12],"snippet",json.dumps(d)[:700])
 except Exception as e:print("FAIL",u,str(e))
