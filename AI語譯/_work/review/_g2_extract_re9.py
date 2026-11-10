# -*- coding: utf-8 -*-
import csv, json, sys
from collections import OrderedDict

P = r"AI語譯/_work/review/report_re9.tsv"
BOOKS = {"資持記", "04_比丘尼鈔"}

rows = []
with open(P, encoding="utf-8", newline="") as f:
    r = csv.reader(f, delimiter="\t")
    header = next(r)
    for i, row in enumerate(r, start=2):
        if len(row) != 10:
            print("BAD", i, len(row), file=sys.stderr)
            continue
        d = dict(zip(header, row))
        if d["book"] not in BOOKS:
            continue
        d["_line"] = i
        rows.append(d)

print("target rows:", len(rows))
print("with suggestion:", sum(1 for d in rows if d["suggestion"].strip()))
print("empty suggestion:", sum(1 for d in rows if not d["suggestion"].strip()))
print("current has newline:", sum(1 for d in rows if "\n" in d["current"]))
print("current has tab:", sum(1 for d in rows if "\t" in d["current"]))

groups = OrderedDict()
for d in rows:
    groups.setdefault((d["book"], d["chunk"], d["seg"]), []).append(d)
print("groups:", len(groups))
print("multi-row groups:", sum(1 for v in groups.values() if len(v) > 1))

for (b, c, s), v in groups.items():
    curs = {x["current"] for x in v}
    if len(curs) > 1:
        print("DIFF CURRENT in group", b, c, s, len(curs))

json.dump([{k: d[k] for k in ("gid","book","chunk","seg","level","cls","problem","suggestion","orig","current","_line")} for d in rows],
          open(r"AI語譯/_work/review/_g2_re9_rows.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("wrote _g2_re9_rows.json")
