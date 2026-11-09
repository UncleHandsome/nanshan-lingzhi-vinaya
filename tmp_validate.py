# -*- coding: utf-8 -*-
import json, csv

data = json.load(open("AI語譯/_work/review/tmp_re8/groups.json", encoding="utf-8"))
lines = open("AI語譯/_work/review/fix_re8_g3.tsv", encoding="utf-8").read().split("\n")
if lines and lines[-1] == "":
    lines.pop()
print("lines:", len(lines))
segs = set()
for n, line in enumerate(lines, 1):
    parts = line.split("\t")
    assert len(parts) == 4, (n, len(parts))
    b, c, s, new = parts
    assert new and "\n" not in new and "\r" not in new
    segs.add((b, c, s))
print("unique keys:", len(segs))

# distribution
from collections import Counter
print(Counter(b for b, c, s, _ in (x.split("\t") for x in lines)))
print(Counter(b for b, c, s in segs))

# which report rows were skipped
skipped = []
for i, (k, gs) in enumerate(data):
    for g in gs:
        pass
# reconstruct: segments with no output
outkeys = segs
noseg = [(i, k) for i, (k, gs) in enumerate(data) if tuple(k) not in outkeys]
print("segments with no output:", noseg)

total_rows = sum(len(gs) for k, gs in data)
print("total report rows:", total_rows)
