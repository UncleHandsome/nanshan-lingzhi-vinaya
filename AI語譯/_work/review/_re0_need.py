# -*- coding: utf-8 -*-
import json, io, sys, os
OUT = r"AI語譯/_work/review/_re0"
ents = json.load(io.open(os.path.join(OUT, "uniq2.json"), encoding="utf-8"))
want = sys.argv[1].split(",")
lines = []
for g in want:
    for e in ents:
        if e["gid"] == g:
            lines.append("### %s %s#%d" % (e["gid"], e["chunk"], e["seg"]))
            lines.append("CUR: " + (e["current"] or ""))
            lines.append("SUG: " + (e["suggestion"] or ""))
            lines.append("")
io.open(os.path.join(OUT, "need.txt"), "w", encoding="utf-8").write("\n".join(lines))
print("lines", len(lines), "chars", sum(len(x) for x in lines))
