# -*- coding: utf-8 -*-
import json, re
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

for d in rows:
    sug = d["suggestion"].strip()
    if not sug: continue
    ops = ops_from_sug(sug)
    n_gai = sug.count("改為")
    if n_gai != len(ops):
        print("L%d s%s gai=%d ops=%d" % (d["_line"], d["seg"], n_gai, len(ops)))
        print("   ", sug)
