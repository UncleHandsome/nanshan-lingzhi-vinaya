# -*- coding: utf-8 -*-
import csv, re
P = r"AI語譯/_work/review/report_re9.tsv"
rows = {}
with open(P, encoding="utf-8", newline="") as f:
    r = csv.reader(f, delimiter="\t")
    header = next(r)
    for i, row in enumerate(r, start=2):
        if len(row) < 10: continue
        d = dict(zip(header, row))
        if d["book"] != "05_拾毗尼義鈔": continue
        d["_line"] = i
        rows[i] = d

for ln in (245, 247, 157):
    d = rows[ln]
    print("="*90)
    print("line", ln, d["chunk"], d["seg"], "cls", d["cls"], "len", len(d["current"]))
    print("PROBLEM:", d["problem"][:300])
    print("SUG:", d["suggestion"][:300])
    print("CURRENT repr head:")
    for k, part in enumerate(d["current"].split("\n")[:12]):
        print(f"  [{k}] len={len(part)} {part[:80]}")
    print("n parts:", len(d["current"].split("\n")))
