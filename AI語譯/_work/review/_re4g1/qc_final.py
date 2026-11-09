# -*- coding: utf-8 -*-
import json, io
rows = json.load(open(r"AI語譯\_work\review\_re4g1\rows.json", encoding="utf-8"))
raw = io.open(r"AI語譯\_work\review\fix_re4_g1.tsv", encoding="utf-8", newline="").read()
lines = raw.split("\n")
if lines[-1] == "": lines.pop()
order = []
cur = {(r["chunk"], r["seg"]): r["current"] for r in rows}
for ln in lines:
    p = ln.split("\t")
    assert len(p) == 4, ln[:40]
    assert p[0] == "02_戒疏"
    assert "\t" not in p[3] and "\r" not in p[3]
    assert p[3].count("「") == p[3].count("」"), (p[1], p[2])
    assert p[3].count("『") == p[3].count("』"), (p[1], p[2])
    assert p[3] != cur[(p[1], p[2])]
    order.append((p[1], p[2]))
# order = report order?
rep_order = []
for r in rows:
    k = (r["chunk"], r["seg"])
    if k not in rep_order: rep_order.append(k)
pos = {k: i for i, k in enumerate(rep_order)}
print("monotonic order:", all(pos[order[i]] < pos[order[i+1]] for i in range(len(order)-1)))
print("lines:", len(lines), "chars:", sum(len(l.split("\t")[3]) for l in lines))
print("first:", lines[0][:110])
print("last :", lines[-1][:110])
print("ALL CHECKS PASSED")
