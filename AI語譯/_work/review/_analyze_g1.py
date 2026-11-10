# -*- coding: utf-8 -*-
import csv, re, sys, os, json
from collections import OrderedDict

P = r"AI語譯/_work/review/report_re9.tsv"
rows = []
with open(P, encoding="utf-8", newline="") as f:
    r = csv.reader(f, delimiter="\t")
    header = next(r)
    for i, row in enumerate(r, start=2):
        if len(row) < 10:
            print("BADROW", i, len(row))
            continue
        d = dict(zip(header, row))
        if d["book"] != "05_拾毗尼義鈔":
            continue
        d["_line"] = i
        rows.append(d)

print("rows", len(rows))
groups = OrderedDict()
for d in rows:
    k = (d["book"], d["chunk"], d["seg"])
    groups.setdefault(k, []).append(d)

print("groups", len(groups))
multi = {k: v for k, v in groups.items() if len(v) > 1}
print("multi-groups", len(multi))
for k, v in multi.items():
    print("  ", k, len(v))

# check identical current within group
for k, v in groups.items():
    cs = set(x["current"] for x in v)
    if len(cs) > 1:
        print("DIFF CURRENT", k, len(cs))

# check empty suggestion
nosug = [d for d in rows if not d["suggestion"].strip()]
print("no suggestion:", len(nosug))
noprob = [d for d in rows if not d["problem"].strip()]
print("no problem:", len(noprob))
emptycur = [d for d in rows if not d["current"].strip()]
print("empty current:", len(emptycur))
# newlines/tabs in current
bad = [d for d in rows if "\n" in d["current"] or "\r" in d["current"]]
print("current with newline:", len(bad))
