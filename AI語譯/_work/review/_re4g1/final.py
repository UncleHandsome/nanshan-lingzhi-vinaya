# -*- coding: utf-8 -*-
import json, io, re
rows = json.load(open(r"AI語譯\_work\review\_re4g1\rows.json", encoding="utf-8"))
lines = io.open(r"AI語譯\_work\review\fix_re4_g1.tsv", encoding="utf-8").read().split("\n")
if lines[-1] == "": lines.pop()
print("lines:", len(lines))
recs = []
for ln in lines:
    p = ln.split("\t")
    assert len(p) == 4 and p[0] == "02_戒疏", (len(p), ln[:40])
    assert "\r" not in ln
    recs.append(p)
cur = {(r["chunk"], r["seg"]): r["current"] for r in rows}
same = [(p[1], p[2]) for p in recs if p[3] == cur[(p[1], p[2])]]
print("unchanged lines:", len(same))
# skipped rows' segs covered by any other row?
skip = [28,34,37,58,134]
for i in skip:
    r = rows[i-1]; k = (r["chunk"], r["seg"])
    others = [j for j, rr in enumerate(rows, 1) if (rr["chunk"], rr["seg"]) == k and j != i]
    print("skip R%d %s is covered by %s" % (i, k, others))
# per-book check and line endings
raw = io.open(r"AI語譯\_work\review\fix_re4_g1.tsv", "rb").read()
print("BOM:", raw[:3] == b"\xef\xbb\xbf", "CR:", b"\r" in raw, "bytes:", len(raw))
print("rows by seg count:", len({(p[1],p[2]) for p in recs}), "dups:", len(recs)-len({(p[1],p[2]) for p in recs}))
