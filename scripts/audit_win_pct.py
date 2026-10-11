import json,urllib.request
u="https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/teams/127?season=2026"
with urllib.request.urlopen(u,timeout=20) as f:d=json.load(f)
print("TEAM_RECORD",json.dumps(d.get("team",{}).get("record",{}))[:2500])
