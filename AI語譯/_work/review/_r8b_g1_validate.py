# -*- coding: utf-8 -*-
import json, io, os, csv

base = os.path.dirname(os.path.abspath(__file__))
rows = json.load(io.open(os.path.join(base, "_r8b_g1_rows.json"), encoding="utf-8"))
base_by = {}
for r in rows:
    base_by[(r["book"], r["chunk"], r["seg"])] = r["current"]

lines = io.open(os.path.join(base, "fix_r8b_g1.tsv"), encoding="utf-8").read().split("\n")
lines = [l for l in lines if l.strip()]
print("lines:", len(lines))
bad = 0
for l in lines:
    f = l.split("\t")
    if len(f) != 4:
        print("BAD COLS", len(f), l[:50]); bad += 1; continue
    k = tuple(f[:3])
    if k not in base_by:
        print("UNKNOWN KEY", k); bad += 1; continue
    if "\n" in f[3] or "\t" in f[3]:
        print("BAD CHAR", k); bad += 1
    cur = base_by[k].replace("\n", "")
    # count differences positions
    i = 0
    while i < min(len(cur), len(f[3])) and cur[i] == f[3][i]:
        i += 1
    j = 0
    while j < min(len(cur), len(f[3])) - i and cur[len(cur)-1-j] == f[3][len(f[3])-1-j]:
        j += 1
    print("%s seg%s len %d->%d  precut=%d  tail=%d" % (k[1], k[2], len(cur), len(f[3]), i, j))
print("bad:", bad)
print("dup keys:", len(lines) - len(set(l.split("\t")[0] + l.split("\t")[1] + l.split("\t")[2] for l in lines)))
