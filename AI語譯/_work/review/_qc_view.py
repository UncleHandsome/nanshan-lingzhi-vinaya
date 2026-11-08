# -*- coding: utf-8 -*-
import json

BASE = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\review"
recs = json.load(open(BASE + r"\_qc_rows.json", encoding="utf-8"))
lookup = {r["gid"]: r for r in recs}
lines = [l.split("\t") for l in open(BASE + r"\fix_qc.tsv", encoding="utf-8").read().split("\n") if l]
outmap = {}
for b, c, s, n in lines:
    rec = [r for r in recs if r["book"] == b and r["chunk"] == c and r["seg"] == s]
    for r in rec:
        outmap[r["gid"]] = n

for gid in ["05-0005", "06-0048", "03-0166", "07-0015", "08-0007", "06-0027", "09-0124"]:
    print("=====", gid)
    print(outmap[gid])
    print()
