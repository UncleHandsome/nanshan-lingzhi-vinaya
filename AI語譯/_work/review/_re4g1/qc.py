# -*- coding: utf-8 -*-
import json, io, re
rows = json.load(open(r"AI語譯\_work\review\_re4g1\rows.json", encoding="utf-8"))
lines = io.open(r"AI語譯\_work\review\fix_re4_g1.tsv", encoding="utf-8").read().rstrip("\n").split("\n")
print("lines:", len(lines))
recs = []
for ln in lines:
    p = ln.split("\t")
    assert len(p) == 4, ("bad fields", len(p), ln[:50])
    recs.append(p)
cur = {}
for r in rows:
    cur[(r["chunk"], r["seg"])] = r["current"]
print("distinct segs in out:", len({(p[1],p[2]) for p in recs}))
# same-seg consistency
seen = {}
for b,c,s,t in recs:
    k=(c,s)
    if k in seen and seen[k]!=t: print("INCONSISTENT", k)
    seen[k]=t
# artifact scan
arts = ["。。","，，","；；","」」","「「","』』","『『","（）","，。","。，","：。","」「"]
for b,c,s,t in recs:
    for a in arts:
        if a in t: print("ARTIFACT", k, a, t[:60])
    if t.count("「")!=t.count("」"): print("QUOTE-UNBAL", c, s, t.count("「"), t.count("」"))
    if t.count("『")!=t.count("』"): print("QUOTE2-UNBAL", c, s)
print("checks done")
# changed length stats
tot_old=tot_new=0
for b,c,s,t in recs:
    o = cur.get((c,s))
    if o is None: print("NO ORIG", c,s); continue
    tot_old += len(o); tot_new += len(t)
print("orig chars", tot_old, "new chars", tot_new)
