# -*- coding: utf-8 -*-
import json, re, io
rows = json.load(open(r"AI語譯/_work/review/_g2_re9_rows.json", encoding="utf-8"))

def ops_from_sug(sug):
    ops = []
    for m in re.finditer(r"將「([^」]*)」([^。；]{0,60}?)改為「([^」]*)」", sug):
        ops.append((m.group(1), m.group(3)))
    if ops:
        return ops
    for m in re.finditer(r"「([^」]*)」([^。；]{0,60}?)改為「([^」]*)」", sug):
        ops.append((m.group(1), m.group(3)))
    return ops

lines = []
for d in rows:
    sug = d["suggestion"].strip()
    if not sug:
        continue
    ops = ops_from_sug(sug)
    if not ops:
        continue
    for a, b in ops:
        n = d["current"].count(a)
        lines.append(f"L{d['_line']} {d['chunk']} s{d['seg']} n={n} | {a} || {b}")
io.open(r"AI語譯/_work/review/_g2_re9_pairs.txt", "w", encoding="utf-8").write("\n".join(lines))
print(len(lines))
