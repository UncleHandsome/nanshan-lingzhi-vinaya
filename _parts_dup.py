import json
from collections import Counter, defaultdict
rows = json.load(open("_parts_rows3.json",encoding="utf-8"))
d=defaultdict(list)
for r in rows:
    d[(r["chunk"],r["seg"])].append((r["idx"],r["gid"],r["level"],r["cls"]))
dups={k:v for k,v in d.items() if len(v)>1}
print("dup count:", len(dups))
for k,v in dups.items(): print(k,v)
print("same gid twice:", [ (r["gid"],r["idx"]) for r in rows if Counter(x["gid"] for x in rows)[r["gid"]]>1][:20])
print("gid counts >1:", {k:v for k,v in Counter(r["gid"] for r in rows).items() if v>1})
