import csv
from pathlib import Path
p=Path("data/processed/player_percentiles/player_percentiles_2026.csv")
rows=list(csv.DictReader(p.open(newline="")))
names={"Jeremy Fears Jr.":"return","Jaxon Kohler":"leave","Coen Carr":"return","Carson Cooper":"leave","Jordan Scott":"return","Kur Teng":"return","Cam Ward":"return","Divine Ugochukwu":"leave","Trey Fort":"leave","Jesse McCulloch":"return","Denham Wojcik":"leave","Colin Walton":"return","Brennan Walton":"return","Nick Sanders":"leave","Anton Bonke":"transfer"}
selected=[]
for r in rows:
 if "michigan state" not in r["team_name"].lower() and not ("charlotte" in r["team_name"].lower() and "bonke" in r["player_name"].lower()):continue
 n=r["player_name"]
 if n not in names:continue
 old=float(r["spats_rating"])
 mins=float(r["mpg_pctile"])
 new=(old-0.05*mins)/0.95
 selected.append((n,names[n],new,old,mins,r["team_name"]))
for x in sorted(selected,key=lambda x:-x[2]):print("RATING",x[0],x[1],f"{x[2]:.6f}","old",f"{x[3]:.6f}","minpct",f"{x[4]:.6f}",x[5])
for label in ("return","leave","transfer"):
 vals=[x[2] for x in selected if x[1]==label]
 print("SUMMARY",label,"count",len(vals),"total",f"{sum(vals):.6f}","average",f"{sum(vals)/len(vals):.6f}" if vals else "NA")
msu=[x[2] for x in selected if x[1]!="transfer"]
print("SUMMARY MSU_2026",len(msu),f"{sum(msu):.6f}",f"{sum(msu)/len(msu):.6f}")
print("SUMMARY PROJECTED",f"{sum(x[2] for x in selected if x[1]!='leave'):.6f}")
