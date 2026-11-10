# -*- coding: utf-8 -*-
import csv, re, sys, json
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

TARGETS = [int(x) for x in sys.argv[1].split(",")]
for ln in TARGETS:
    d = rows[ln]
    cur = d["current"].replace("\n", "")
    print("="*110)
    print(f"### line={ln} {d['chunk']} seg={d['seg']} {d['level']} {d['cls']}")
    print("PROB:", d["problem"])
    print("SUG :", d["suggestion"])
    qs = re.findall(r"「([^」]{2,})」", d["problem"] + " || " + d["suggestion"])
    seen = set()
    for q in qs:
        if q in seen: continue
        seen.add(q)
        c = cur.count(q)
        print(f"  quote({len(q)}) x{c}: {q[:80]}")
    # print context around each found quote of len>=6
    printed = 0
    for q in seen:
        if len(q) < 6: continue
        if cur.count(q) == 0: continue
        i = cur.find(q)
        print(f"  CTX[{q[:20]}]: ...{cur[max(0,i-120):i+len(q)+120]}...")
        printed += 1
        if printed >= 3: break
