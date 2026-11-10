# -*- coding: utf-8 -*-
import csv, re, os
from collections import defaultdict

P = r"AI語譯/_work/review/report_re9.tsv"
rows = []
with open(P, encoding="utf-8", newline="") as f:
    r = csv.reader(f, delimiter="\t")
    header = next(r)
    for row in r:
        if len(row) < 10: continue
        d = dict(zip(header, row))
        if d["book"] != "05_拾毗尼義鈔": continue
        rows.append(d)

files = {}
for fn in os.listdir(r"AI語譯/out/05_拾毗尼義鈔"):
    if fn.endswith(".txt"):
        chunk = fn[:-4]
        files[chunk] = open(os.path.join(r"AI語譯/out/05_拾毗尼義鈔", fn), encoding="utf-8").read().split("\n")

# for each chunk, list non-empty line indices -> paragraph no
stats = defaultdict(list)
for d in rows:
    chunk = d["chunk"]
    if chunk not in files: 
        print("NOFILE", chunk); continue
    lines = files[chunk]
    parts = d["current"].split("\n")
    key = parts[0][:25]
    idx = next((i for i, ln in enumerate(lines) if ln.startswith(key)), None)
    if idx is None:
        stats[chunk].append((d["seg"], None, len(parts)))
        continue
    # paragraph number (1-based over non-empty)
    pno = sum(1 for ln in lines[:idx+1] if ln.strip())
    stats[chunk].append((int(d["seg"]), pno, len(parts)))

for chunk in sorted(stats):
    bad = [(s, p, n) for s, p, n in stats[chunk] if p is not None and s != p]
    print(f"{chunk}: rows={len(stats[chunk])} mismatches={len(bad)}")
    for s, p, n in bad[:20]:
        print(f"   seg={s} paragraph={p} parts={n}")
