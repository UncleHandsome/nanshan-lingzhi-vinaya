import json, io, sys, collections
sys.path.insert(0, r"AI語譯/_work/review")
from _re0_decisions import D
OUT = r"AI語譯/_work/review/_re0"
ents = json.load(io.open(OUT + "/uniq2.json", encoding="utf-8"))
c = collections.Counter(e["gid"] for e in ents)
for gid in D:
    if c[gid] > 1:
        print(gid, c[gid], [e["type"] for e in ents if e["gid"]==gid])
