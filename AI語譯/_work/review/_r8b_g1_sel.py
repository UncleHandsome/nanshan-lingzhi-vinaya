# -*- coding: utf-8 -*-
import json, io, os, sys

base = os.path.dirname(os.path.abspath(__file__))
rows = json.load(io.open(os.path.join(base, "_r8b_g1_rows.json"), encoding="utf-8"))
idxs = [int(x) for x in sys.argv[1].split(",")]
out = io.open(os.path.join(base, "_r8b_g1_sel.txt"), "w", encoding="utf-8")
for i in idxs:
    r = rows[i]
    out.write("### %d | %s | %s | seg %s\n" % (i, r["book"], r["chunk"], r["seg"]))
    out.write("P: %s\n" % r["problem"].replace("\n", " "))
    out.write("S: %s\n" % r["suggestion"].replace("\n", " "))
    out.write("ORIG: %s\n" % r["orig"].replace("\n", " "))
    out.write("CURR: %s\n\n" % r["current"].replace("\n", " ⏎ "))
out.close()
print("ok", idxs)
