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

out = []
for d in rows:
    sug = d["suggestion"].strip()
    if not sug:
        out.append("=" * 100)
        out.append(f"L{d['_line']} {d['book']} {d['chunk']} s{d['seg']} {d['level']} {d['cls']}  <<EMPTY SUG>>")
        out.append("PROBLEM: " + d["problem"])
        continue
    ops = ops_from_sug(sug)
    if ops:
        # report rows whose A not present
        miss = [(a, b) for a, b in ops if a not in d["current"]]
        if not miss:
            continue
    out.append("=" * 100)
    out.append(f"L{d['_line']} {d['book']} {d['chunk']} s{d['seg']} {d['level']} {d['cls']}  <<{'NOPAT' if not ops else 'A-MISSING'}>>")
    out.append("PROBLEM: " + d["problem"])
    out.append("SUG: " + sug)
    if ops:
        for a, b in ops:
            out.append(f"  A: {a}")
            out.append(f"  B: {b}")
    out.append("CURRENT: " + d["current"].replace("\n", "\\n"))
io.open(r"AI語譯/_work/review/_g2_re9_manual.txt", "w", encoding="utf-8").write("\n".join(out))
print("lines", len(out), "chars", sum(len(x) for x in out))
