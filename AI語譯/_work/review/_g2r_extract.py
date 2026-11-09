# -*- coding: utf-8 -*-
"""Extract the 94 rows for 03_業疏 / 資持記 / 01_行事鈔 from report_re5.tsv,
group them by (book,chunk,seg), and dump per-group readable text."""
import csv, json, os
from collections import Counter, OrderedDict

SRC = r"AI語譯\_work\review\report_re5.tsv"
BOOKS = {"03_業疏", "資持記", "01_行事鈔"}
OUTDIR = r"AI語譯\_work\review\_g2r"
os.makedirs(OUTDIR, exist_ok=True)

rows = []
with open(SRC, "r", encoding="utf-8-sig", newline="") as f:
    r = csv.reader(f, delimiter="\t")
    header = next(r)
    for i, row in enumerate(r, start=1):
        if not row or len(row) < 10:
            continue
        d = dict(zip(header, row))
        if d["book"] in BOOKS:
            d["_idx"] = i
            rows.append(d)

print("rows:", len(rows))
print("by book:", Counter(d["book"] for d in rows))
print("levels:", Counter(d["level"] for d in rows))
print("cls:", Counter(d["cls"] for d in rows))

groups = OrderedDict()
for d in rows:
    k = (d["book"], d["chunk"], d["seg"])
    groups.setdefault(k, []).append(d)
print("groups(unique segs):", len(groups))
print("multi-problem groups:", sum(1 for v in groups.values() if len(v) > 1))

# how many rows have empty suggestion
print("no-suggestion rows:", [d["_idx"] for d in rows if not d["suggestion"].strip()])

json.dump(rows, open(os.path.join(OUTDIR, "rows.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

# dump per group
with open(os.path.join(OUTDIR, "groups.txt"), "w", encoding="utf-8") as f:
    for gi, (k, v) in enumerate(groups.items(), start=1):
        f.write("=" * 100 + "\n")
        f.write(f"GROUP {gi}  book={k[0]} chunk={k[1]} seg={k[2]}  rows={[d['_idx'] for d in v]}\n")
        f.write(f"orig: {v[0]['orig']}\n")
        for d in v:
            f.write(f"--- row {d['_idx']} [{d['level']}/{d['cls']}]\n")
            f.write(f"PROBLEM: {d['problem']}\n")
            f.write(f"SUGGEST: {d['suggestion']}\n")
        f.write(f"CURRENT({len(v[0]['current'])}): {v[0]['current']}\n")

# short index for browsing
with open(os.path.join(OUTDIR, "index.tsv"), "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, delimiter="\t", lineterminator="\n")
    for d in rows:
        w.writerow([d["_idx"], d["book"], d["chunk"], d["seg"], d["level"], d["cls"],
                    len(d["current"]), d["orig"][:40],
                    d["problem"][:60], d["suggestion"][:60]])
print("dumped")
