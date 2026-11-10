# -*- coding: utf-8 -*-
"""Dump clean ops with local context for review."""
import re, io, json, os
OUT = r"AI語譯/_work/review/_re0"
ents = json.load(io.open(os.path.join(OUT, "uniq2.json"), encoding="utf-8"))
lines = []
n = 0
for e in sorted(ents, key=lambda x: (x["book"], x["chunk"], x["seg"], x["gid"])):
    pairs = e["pairs"]
    kind = pairs[0][0]
    cur = e["current"] or ""
    if kind in ("將A改為B", "A改為B", "刪除") and all((p[1] or "") in cur for p in pairs):
        n += 1
        for old, new in [(p[1], p[2]) for p in pairs]:
            i = cur.find(old)
            lines.append("### %s seg=%d %s" % (e["gid"], e["seg"], e["type"]))
            lines.append("  OLD: " + old)
            lines.append("  NEW: " + new)
            lines.append("  CTX: …" + cur[max(0, i - 40):i] + "【" + cur[i:i + len(old)] + "】" + cur[i + len(old):i + len(old) + 40] + "…")
            lines.append("")
io.open(os.path.join(OUT, "clean_ctx.txt"), "w", encoding="utf-8").write("\n".join(lines))
print("clean ops:", n, "lines:", len(lines))
