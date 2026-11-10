# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r"AI語譯/_work/review")
from _build3_g1 import main

out, stats = main()

applied_rows = sum(1 for s in stats if s["applied"] > 0)
skipped_rows = sum(1 for s in stats if s["applied"] == 0)

recs = []
for key, txt, base, per in out:
    b = base.rstrip("\n").replace("\n", "")
    if txt == b:
        continue
    assert "\t" not in txt, key
    assert "\n" not in txt and "\r" not in txt, key
    recs.append((key[0], key[1], int(key[2]), txt))

recs.sort(key=lambda r: (r[0], r[1], r[2]))

path = r"AI語譯/_work/review/fix_re9_g1.tsv"
with open(path, "w", encoding="utf-8", newline="\n") as f:
    for book, chunk, seg, txt in recs:
        f.write("\t".join([book, chunk, str(seg), txt]) + "\n")

print("wrote", path)
print("lines:", len(recs))
print("report rows applied:", applied_rows, "skipped:", skipped_rows)
