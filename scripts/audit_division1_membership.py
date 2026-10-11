"""Audit season-specific ESPN Division I membership before rebuilding SPATS ratings."""
import json,urllib.request
for yr in (2005,2015,2025,2026):
 url=f"https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/teams?groups=50&limit=500&season={yr}"
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"SPATS-research/1.0"}),timeout=30) as f: d=json.load(f)
  teams=[t["team"] for s in d["sports"] for l in s["leagues"] for t in l["teams"]]
  print("AUDIT",yr,"count",len(teams),"ids",",".join(t["id"] for t in teams[:8]),"shaw",any("Shaw" in t.get("displayName","") for t in teams))
 except Exception as e:print("ERROR",yr,str(e))
