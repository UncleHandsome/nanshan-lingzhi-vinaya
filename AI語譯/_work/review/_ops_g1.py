# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r"AI語譯/_work/review")
import importlib, _build3_g1 as B
importlib.reload(B)

rows = B.load()
groups = {}
for d in rows:
    groups.setdefault((d["book"], d["chunk"], d["seg"]), []).append(d)

lines = []
for key, grp in groups.items():
    cur = grp[0]["current"]
    entries = []
    for d in grp:
        kind, ops = B.ops_for(d)
        for a, b in ops:
            done = False
            for aa in (a, B.norm(a)):
                if aa in cur:
                    cur = cur.replace(aa, b, 1)
                    entries.append((d["_line"], a, b))
                    done = True
                    break
            if not done:
                entries.append((d["_line"], "!MISS " + a, ""))
    if not entries: continue
    lines.append("="*110)
    lines.append(f"### {key[1]} seg={key[2]}")
    for ln, a, b in entries:
        lines.append(f"  [row {ln}] A({len(a)}): {a}")
        lines.append(f"            B({len(b)}): {b}")
open(r"AI語譯/_work/review/_ops_g1.txt","w",encoding="utf-8").write("\n".join(lines))
print("lines", len(lines))
