# -*- coding: utf-8 -*-
import json, re, io, os
rows = json.load(open(r"AI語譯\_work\review\_re4g1\rows.json", encoding="utf-8"))
print("rows", len(rows))
segs = {}
for r in rows:
    k = (r["chunk"], r["seg"])
    segs.setdefault(k, []).append(r)
print("distinct segs", len(segs))
print("max rows per seg", max(len(v) for v in segs.values()))
# how many rows where current == tr
same = sum(1 for r in rows if r["tr"] == r["current"])
print("current==tr:", same, "diff:", len(rows)-same)
# detect simple 將X改為Y
n_old_in_cur = 0; n_old_not = 0; n_other = 0
for r in rows:
    s = r["suggestion"]; cur = r["current"]
    m = re.match(r"^將「(.+?)」改為「(.+?)」", s) or re.search(r"將「(.+?)」改為「(.+?)」", s)
    if m:
        old = m.group(1)
        if old in cur: n_old_in_cur += 1
        else: n_old_not += 1
    else:
        n_other += 1
print("simple: old-in-current", n_old_in_cur, "old-NOT-in-current", n_old_not, "non-simple", n_other)
