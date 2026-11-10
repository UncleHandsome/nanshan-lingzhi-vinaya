import csv, sys, json, re
sys.stdout.reconfigure(encoding="utf-8")
rows = json.load(open("_g2rows.json", encoding="utf-8"))
keep=[(i,r) for i,r in enumerate(rows) if "重複貼上" not in r[6]]
print("kept", len(keep))
nosug=[(i,r) for i,r in keep if not r[7].strip()]
print("nosug", len(nosug), [(r[2],r[3],r[6][:40]) for i,r in nosug])
# group by seg
from collections import OrderedDict
g=OrderedDict()
for i,r in keep:
    g.setdefault((r[2],r[3]), []).append(i)
print("unique segs", len(g))
for k,v in g.items():
    if len(v)>1: print(k, v)
json.dump([[i,r] for i,r in keep], open("_g2keep.json","w",encoding="utf-8"), ensure_ascii=False)
