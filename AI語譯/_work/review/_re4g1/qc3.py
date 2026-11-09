# -*- coding: utf-8 -*-
import json, io, re
rows = json.load(open(r"AI語譯\_work\review\_re4g1\rows.json", encoding="utf-8"))
lines = io.open(r"AI語譯\_work\review\fix_re4_g1.tsv", encoding="utf-8").read().rstrip("\n").split("\n")
cur = {(r["chunk"], r["seg"]): r["current"] for r in rows}
pats = ["。。","，，","；；","：。","，。","。，","：，","；。","，，","、、","的的","了了","是是","在在"]
issues = 0
for ln in lines:
    b,c,s,t = ln.split("\t")
    o = cur[(c,s)]
    for p in pats:
        if p in t:
            k = t.find(p)
            print("PUNCT", c, s, repr(p), t[max(0,k-25):k+25]); issues += 1
    # doubled word of 2 chars crossing boundary is hard; skip
print("punctuation issues:", issues)
# show all changed spans in context compactly (15 chars each side)
print("\n---- compact contexts ----")
for ln in lines:
    b,c,s,t = ln.split("\t")
    o = cur[(c,s)]
    if t == o: continue
    # find first/last differing index
    i = 0
    while i < min(len(o), len(t)) and o[i] == t[i]: i += 1
    j = 0
    while j < min(len(o), len(t))-i and o[len(o)-1-j] == t[len(t)-1-j]: j += 1
    print("%s/%s: …%s⟦%s⟧%s…" % (c, s, t[max(0,i-20):i], t[i:len(t)-j], t[len(t)-j:len(t)-j+20]))
