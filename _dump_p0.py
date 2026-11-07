# -*- coding: utf-8 -*-
import csv, os, io

base = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(base, "AI語譯", "_work", "review", "report_t2.tsv")

with open(p, encoding="utf-8") as f:
    rows = list(csv.DictReader(f, delimiter="\t"))

out = []
out.append("TOTAL rows: %d" % len(rows))
from collections import Counter
out.append("levels: " + repr(Counter(r["level"] for r in rows)))
out.append("statuses: " + repr(Counter(r["status"] for r in rows)))

p0 = [r for r in rows if r["level"] == "P0"]
out.append("P0 count: %d" % len(p0))
out.append("")

for i, r in enumerate(p0):
    out.append("=" * 110)
    out.append("[%d] %s | %s | seg %s | cls=%s | status=%s" % (
        i, r["book"], r["chunk"], r["seg"], r["cls"], r["status"]))
    for k in ["problem", "suggestion", "orig", "tr", "current"]:
        v = r.get(k) or ""
        out.append("--- %s (len=%d) ---" % (k, len(v)))
        out.append(v)
    out.append("")

with open(os.path.join(base, "_p0_dump.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(out))

print("wrote", len(out), "lines; P0 =", len(p0))
