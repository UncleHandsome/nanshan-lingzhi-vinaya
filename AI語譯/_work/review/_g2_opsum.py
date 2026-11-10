# -*- coding: utf-8 -*-
import json, re, io
from collections import OrderedDict, Counter

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

# group rows
groups = OrderedDict()
for d in rows:
    groups.setdefault((d["book"], d["chunk"], d["seg"]), []).append(d)

out = []
cnt = Counter()
for key, rs in groups.items():
    b, c, s = key
    out.append(f"##### {b} {c} seg={s} rows={len(rs)}")
    for d in rs:
        sug = d["suggestion"].strip()
        line = f"[{d['_line']}] {d['level']} {d['cls']}"
        if not sug:
            out.append(line + "  <<EMPTY SUG>>")
            cnt["empty"] += 1
            continue
        ops = ops_from_sug(sug)
        if not ops:
            out.append(line + "  <<NO-PATTERN>>")
            cnt["nopat"] += 1
            continue
        det = []
        for a, bb in ops:
            na = d["current"].count(a)
            nb = d["current"].count(bb)
            det.append(f"A({len(a)})x{na} -> B({len(bb)})x{nb}")
            cnt["cnt%d" % min(na, 5)] += 1
        out.append(line + "  " + "; ".join(det))
io.open(r"AI語譯/_work/review/_g2_re9_opsum.txt", "w", encoding="utf-8").write("\n".join(out))
print(cnt)
print("groups", len(groups))
print("groups with nopat", sum(1 for rs in groups.values() if any(not ops_from_sug(d["suggestion"].strip()) for d in rs if d["suggestion"].strip())))
