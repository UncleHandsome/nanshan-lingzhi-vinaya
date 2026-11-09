# -*- coding: utf-8 -*-
import json, io, os
base = os.path.dirname(os.path.abspath(__file__))
rows = json.load(io.open(os.path.join(base, "_r8b_g1_rows.json"), encoding="utf-8"))
out = io.open(os.path.join(base, "_nl_check.txt"), "w", encoding="utf-8")
for i, r in enumerate(rows):
    c = r["current"]
    if "\n" in c:
        out.write("ROW %d %s %s seg%s nls=%d\n" % (i, r["book"], r["chunk"], r["seg"], c.count("\n")))
        for j, ch in enumerate(c):
            if ch == "\n":
                out.write("   ...%s ||| %s...\n" % (c[max(0,j-30):j], c[j+1:j+30]))
out.close()
print("ok")
