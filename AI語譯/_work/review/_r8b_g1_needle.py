# -*- coding: utf-8 -*-
import json, io, os, sys

base = os.path.dirname(os.path.abspath(__file__))
rows = json.load(io.open(os.path.join(base, "_r8b_g1_rows.json"), encoding="utf-8"))
i = int(sys.argv[1])
needles = sys.argv[2].split("|")
c = rows[i]["current"]
out = io.open(os.path.join(base, "_r8b_g1_sel.txt"), "w", encoding="utf-8")
out.write("ROW %d len=%d\n" % (i, len(c)))
for nd in needles:
    pos = 0
    hit = False
    while True:
        j = c.find(nd, pos)
        if j < 0:
            break
        hit = True
        a = max(0, j - 120); b = min(len(c), j + len(nd) + 120)
        out.write("[%s] ...%s...\n\n" % (nd, c[a:b]))
        pos = j + 1
    if not hit:
        out.write("[%s] NOT FOUND\n\n" % nd)
out.close()
print("ok")
