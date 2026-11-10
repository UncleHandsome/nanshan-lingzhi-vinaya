# -*- coding: utf-8 -*-
import io, json
rows = json.load(open(r"AI語譯/_work/review/_g2_re9_rows.json", encoding="utf-8"))
base = {(d["book"], d["chunk"], d["seg"]): d["current"].replace("\n", "") for d in rows}
deltas = []
for l in io.open(r"AI語譯/_work/review/fix_re9_g2.tsv", encoding="utf-8").read().split("\n"):
    if not l.strip():
        continue
    b, c, s, new = l.split("\t")
    old = base[(b, c, s)]
    deltas.append((len(new) - len(old), b, c, s, len(old), len(new)))
deltas.sort()
print("--- most shrank ---")
for d in deltas[:10]:
    print(d)
print("--- most grew ---")
for d in deltas[-8:]:
    print(d)
