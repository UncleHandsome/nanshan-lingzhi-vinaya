import json, sys
sys.path.insert(0,".")
from _parts_ops import OPS
rows = json.load(open("_parts_rows3.json",encoding="utf-8"))
allidx=[r["idx"] for r in rows]
missing=[i for i in allidx if i not in OPS]
print("OPS:",len(OPS),"all:",len(allidx),"missing:",len(missing))
print(missing)
