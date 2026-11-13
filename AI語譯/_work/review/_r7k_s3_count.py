# -*- coding: utf-8 -*-
"""統計 edits JSON：每檔改段數、ops 數。"""
import os, sys, json, io, glob, re

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
D = os.path.join(ROOT, "AI語譯", "_work", "review")

rows = {}
for p in sorted(glob.glob(os.path.join(D, "_r7k_s3_e_*.json"))):
    d = json.loads(io.open(p, encoding="utf-8").read())
    for chunk, segs in d.items():
        for no, e in segs.items():
            n = no.split("-")[0]
            rows.setdefault(n, {"segs": 0, "ops": 0})
            rows[n]["segs"] += 1
            rows[n]["ops"] += len(e["ops"])

tot_s = tot_o = 0
for n in sorted(rows):
    r = rows[n]
    print("%s\t%d\t%d" % (n, r["segs"], r["ops"]))
    tot_s += r["segs"]
    tot_o += r["ops"]
print("TOTAL\t%d\t%d" % (tot_s, tot_o))
