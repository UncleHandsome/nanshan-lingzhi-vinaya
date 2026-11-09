# -*- coding: utf-8 -*-
import json, io

rows = json.load(io.open("_r8_rows.json", encoding="utf-8"))
for part in range(4):
    lo = part * 16
    hi = min(lo + 16, len(rows))
    with io.open("_r8_dump_%d.txt" % part, "w", encoding="utf-8") as f:
        for r in rows[lo:hi]:
            f.write("### %02d %s %s seg=%s cls=%s\n" % (r["i"], r["gid"], r["chunk"], r["seg"], r["cls"]))
            f.write("PROBLEM: %s\n" % r["problem"])
            f.write("SUG: %s\n" % r["suggestion"])
            f.write("CUR: %s\n\n" % r["current"])
print("done")
