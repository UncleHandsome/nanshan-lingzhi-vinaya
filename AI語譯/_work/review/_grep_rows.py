# -*- coding: utf-8 -*-
import csv, re, sys
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

# usage: python _grep_rows.py LINE "probe1" "probe2" ...
ln = int(sys.argv[1])
d = rows[ln]
cur = d["current"].replace("\n", "")
print(f"### line={ln} {d['chunk']} seg={d['seg']} len={len(cur)}")
for probe in sys.argv[2:]:
    c = cur.count(probe)
    print(f"--- probe x{c}: {probe}")
    st = 0
    for _ in range(min(c, 3)):
        i = cur.find(probe, st)
        if i == -1: break
        print("    ...", cur[max(0,i-90):i+len(probe)+90], "...")
        st = i + 1
