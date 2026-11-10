# -*- coding: utf-8 -*-
import json, re, sys
from collections import Counter, OrderedDict

rows = json.load(open(r"AI語譯/_work/review/_g2_re9_rows.json", encoding="utf-8"))

def ops_from_sug(sug):
    """Extract (A,B) pairs from suggestions of form 將「A」...改為「B」."""
    ops = []
    # 將「A」…改為「B」
    for m in re.finditer(r"將「([^」]*)」([^。；]{0,60}?)改為「([^」]*)」", sug):
        ops.append((m.group(1), m.group(3)))
    if ops:
        return ops
    for m in re.finditer(r"「([^」]*)」([^。；]{0,60}?)改為「([^」]*)」", sug):
        ops.append((m.group(1), m.group(3)))
    return ops

cnt = Counter()
noop = []
for d in rows:
    sug = d["suggestion"].strip()
    if not sug:
        cnt["EMPTY_SUG"] += 1
        continue
    ops = ops_from_sug(sug)
    if not ops:
        cnt["NO_PATTERN"] += 1
        noop.append(d)
        continue
    d["_ops"] = ops
    missing = [a for a, b in ops if a not in d["current"]]
    if missing:
        cnt["A_NOT_IN_CURRENT"] += 1
    else:
        cnt["A_OK"] += 1
    cnt["ops%d" % len(ops)] += 1

print(cnt)
print("no-pattern:", len(noop))
with open(r"AI語譯/_work/review/_g2_re9_nopat.txt", "w", encoding="utf-8") as f:
    for d in noop:
        f.write("=" * 100 + "\n")
        f.write(f"line={d['_line']} {d['book']} {d['chunk']} seg={d['seg']} {d['level']} {d['cls']}\n")
        f.write("PROBLEM: " + d["problem"] + "\n")
        f.write("SUG: " + d["suggestion"] + "\n")
        f.write("CURRENT: " + d["current"] + "\n")
print("wrote _g2_re9_nopat.txt")
