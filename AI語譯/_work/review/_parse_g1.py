# -*- coding: utf-8 -*-
import csv, re, json
from collections import OrderedDict

P = r"AI語譯/_work/review/report_re9.tsv"
rows = []
with open(P, encoding="utf-8", newline="") as f:
    r = csv.reader(f, delimiter="\t")
    header = next(r)
    for i, row in enumerate(r, start=2):
        if len(row) < 10:
            continue
        d = dict(zip(header, row))
        if d["book"] != "05_拾毗尼義鈔":
            continue
        d["_line"] = i
        rows.append(d)

groups = OrderedDict()
for d in rows:
    k = (d["book"], d["chunk"], d["seg"])
    groups.setdefault(k, []).append(d)

def find_pat(sug):
    """return list of (A,B,kind) replacement ops"""
    ops = []
    s = sug
    # 1) 將「A」改為「B」
    # quotes: 「」 outer, inner may contain 『』 or 《》
    pat = re.compile(r"將「([^」]*)」([^。；]{0,40}?)改為「([^」]*)」")
    for m in pat.finditer(s):
        ops.append((m.group(1), m.group(3), "AtoB"))
    if ops:
        return ops
    pat2 = re.compile(r"「([^」]*)」([^。；]{0,40}?)改為「([^」]*)」")
    for m in pat2.finditer(s):
        ops.append((m.group(1), m.group(3), "AtoB"))
    return ops

acts = []
nop = []
for d in rows:
    sug = d["suggestion"].strip()
    cur = d["current"]
    if not sug:
        nop.append(d)
        continue
    ops = find_pat(sug)
    if not ops:
        nop.append(d)
        continue
    ok = all(a in cur for a, b, k in ops)
    if not ok:
        d["_ops"] = ops
        acts.append((d, "NOTFOUND", ops))
    else:
        d["_ops"] = ops
        acts.append((d, "OK", ops))

from collections import Counter
print(Counter(x[1] for x in acts))
print("no-pattern rows:", len(nop))
with open(r"AI語譯/_work/review/_nopattern_g1.txt", "w", encoding="utf-8") as f:
    for d in nop:
        f.write("=" * 80 + "\n")
        f.write(f"line={d['_line']} {d['chunk']} seg={d['seg']} {d['level']} {d['cls']}\n")
        f.write("PROBLEM: " + d["problem"] + "\n")
        f.write("SUG: " + d["suggestion"] + "\n")
print("wrote _nopattern_g1.txt")
