# -*- coding: utf-8 -*-
import json, io, os, re, sys

base = os.path.dirname(os.path.abspath(__file__))
rows = json.load(io.open(os.path.join(base, "_r8b_g1_rows.json"), encoding="utf-8"))
idxs = [int(x) for x in sys.argv[1].split(",")]
mode = sys.argv[2] if len(sys.argv) > 2 else "full"
out = io.open(os.path.join(base, "_r8b_g1_sel.txt"), "w", encoding="utf-8")
for i in idxs:
    r = rows[i]
    c = r["current"]
    out.write("### %d | %s %s seg%s | len=%d\n" % (i, r["book"], r["chunk"], r["seg"], len(c)))
    out.write("P: %s\n" % r["problem"].replace("\n", " "))
    out.write("S: %s\n" % r["suggestion"].replace("\n", " "))
    if mode == "full":
        out.write("C: %s\n" % c.replace("\n", " ⏎ "))
    else:
        # print windows around suggestion quotes
        qs = re.findall(r'「([^」]{2,80})」', r["suggestion"])
        for q in qs:
            for m in re.finditer(re.escape(q), c):
                a = max(0, m.start() - 60); b = min(len(c), m.end() + 60)
                out.write("  [HIT %s] ...%s...\n" % (q[:10], c[a:b].replace("\n", " ⏎ ")))
    out.write("\n")
out.close()
print("ok")
