# -*- coding: utf-8 -*-
import json, sys, re
sys.path.insert(0, ".")
import importlib
import _parts_ops
importlib.reload(_parts_ops)
from _parts_ops import OPS

rows = json.load(open("_parts_rows3.json", encoding="utf-8"))
by = {r["idx"]: r for r in rows}

fail = []
notes = []
newmap = {}
for idx in sorted(OPS):
    r = by[idx]
    cur = r["current"]
    new = cur
    for old, rep, cnt in OPS[idx]:
        if old == "__APPEND__":
            if rep and rep in new:
                fail.append((idx, r["gid"], "append-dup", 1))
            new = new + rep
            continue
        if old == "__PREPEND__":
            if rep and rep in new:
                fail.append((idx, r["gid"], "prepend-dup", 1))
            new = rep + new
            continue
        c = new.count(old)
        if c != cnt:
            fail.append((idx, r["gid"], "count=%d expect=%d %r" % (c, cnt, old[:30]), 0))
            continue
        new = new.replace(old, rep)
    if new != cur:
        newmap[idx] = new

lines = ["FAILURES: %d" % len(fail)]
for f in fail:
    lines.append("  %s" % (f,))
lines.append("")
lines.append("CHANGED: %d" % len(newmap))
from collections import defaultdict
d = defaultdict(list)
for idx in newmap:
    r = by[idx]
    d[(r["chunk"], r["seg"])].append(idx)
for k, v in sorted(d.items()):
    if len(v) > 1:
        lines.append("MERGE %s <- idx %s" % (k, v))
open("_parts_verify.txt", "w", encoding="utf-8").write("\n".join(lines))
json.dump({str(k): v for k, v in newmap.items()}, open("_parts_new.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("done changed=%d fail=%d" % (len(newmap), len(fail)))
