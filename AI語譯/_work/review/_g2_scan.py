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

print("--- suspicious ops ---")
for d in rows:
    sug = d["suggestion"].strip()
    if not sug:
        continue
    ops = ops_from_sug(sug)
    for a, b in ops:
        flags = []
        if a == b: flags.append("SAME")
        if len(a) <= 3: flags.append("SHORT")
        if a.endswith("「"): flags.append("TRUNC-A")
        if a.endswith("……"): flags.append("ELLIP-A")
        if b.endswith("……"): flags.append("ELLIP-B")
        if "……" in sug: flags.append("ELLIP-SUG")
        if b in a: flags.append("B-in-A")
        if flags:
            print("L%d s%s %s | A=%r B=%r | %s" % (d["_line"], d["seg"], d["chunk"], a, b, ",".join(flags)))
            print("   SUG:", sug)
print()
print("--- suggestions with 或 ---")
for d in rows:
    sug = d["suggestion"].strip()
    if "或" in sug and ops_from_sug(sug):
        print("L%d s%s | %s" % (d["_line"], d["seg"], sug))
