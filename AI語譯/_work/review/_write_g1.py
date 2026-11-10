# -*- coding: utf-8 -*-
import sys, io
sys.path.insert(0, r"AI語譯/_work/review")
from _build3_g1 import main

out, stats = main()
lines = []
skipped_rows = 0
applied_rows = 0
for s in stats:
    if s["applied"] > 0: applied_rows += 1
    else: skipped_rows += 1

for key, txt, base, per in out:
    b = base.rstrip("\n").replace("\n", "")
    if txt == b:
        continue
    assert "\t" not in txt and "\n" not in txt, key
    lines.append("\t".join([key[0], key[1], key[2], txt]))

path = r"AI語譯/_work/review/fix_re9_g1.tsv"
with open(path, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(lines) + "\n")
print("wrote", path, "rows:", len(lines))
print("input rows applied:", applied_rows, "skipped:", skipped_rows, "total:", applied_rows+skipped_rows)
