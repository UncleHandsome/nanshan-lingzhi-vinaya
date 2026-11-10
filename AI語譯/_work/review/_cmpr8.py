# -*- coding: utf-8 -*-
import csv, json
from collections import OrderedDict

def load(rep):
    rows = []
    with open(rep, encoding="utf-8", newline="") as f:
        r = csv.reader(f, delimiter="\t")
        header = next(r)
        for row in r:
            if len(row) < 10: continue
            rows.append(dict(zip(header, row)))
    return rows

rep8 = load(r"AI語譯/_work/review/report_re8.tsv")
print("re8 rows", len(rep8))
nl = [d for d in rep8 if "\n" in d["current"]]
print("re8 current-with-newline rows:", len(nl))

fix = {}
with open(r"AI語譯/_work/review/fix_re8_g1.tsv", encoding="utf-8") as f:
    for line in f:
        line = line.rstrip("\n")
        if not line: continue
        parts = line.split("\t")
        if len(parts) != 4:
            print("BAD fix line", len(parts)); continue
        fix[(parts[0], parts[1], parts[2])] = parts[3]
print("fix keys", len(fix))

n = 0
for d in nl:
    k = (d["book"], d["chunk"], d["seg"])
    if k in fix:
        n += 1
        print("="*80)
        print(k, "orig parts", len(d["current"].split("\n")))
        for i, p in enumerate(d["current"].split("\n")):
            print(f"  cur[{i}] {p[:60]}")
        print("  FIX:", fix[k][:300])
print("matched nl rows:", n)
