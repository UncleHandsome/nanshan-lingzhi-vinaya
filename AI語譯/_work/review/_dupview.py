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

for ln in (245, 246, 248, 251):
    d = rows[ln]
    parts = d["current"].split("\n")
    print("="*100)
    print("line", ln, d["chunk"], "seg", d["seg"], "parts", len(parts), "total", len(d["current"]))
    print("SUG:", d["suggestion"])
    for i, p in enumerate(parts):
        print(f"[{i:2d}] len={len(p):4d} {p[:70]}")
