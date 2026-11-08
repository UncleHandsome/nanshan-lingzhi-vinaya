import csv, json, os, sys

path = r"AI語譯\_work\review\report_new.tsv"
rows = []
with open(path, "r", encoding="utf-8-sig", newline="") as f:
    r = csv.reader(f, delimiter="\t")
    header = next(r)
    for row in r:
        if not row or len(row) < 12:
            continue
        d = dict(zip(header, row))
        if d["book"] == "01_行事鈔":
            rows.append(d)

print("count:", len(rows))
# check for dup keys
keys = [(d["book"], d["chunk"], d["seg"]) for d in rows]
print("unique keys:", len(set(keys)))
from collections import Counter
c = Counter(keys)
for k, v in c.items():
    if v > 1:
        print("DUP:", k, v)
print("levels:", Counter(d["level"] for d in rows))
print("cls:", Counter(d["cls"] for d in rows))
print("conf:", Counter(d["conf"] for d in rows))

os.makedirs(r"AI語譯\_work\review\_g2x", exist_ok=True)
with open(r"AI語譯\_work\review\_g2x\rows.json", "w", encoding="utf-8") as f:
    json.dump(rows, f, ensure_ascii=False, indent=1)

# also dump number of rows per line-index ordering
print("chunks:", sorted(set(d["chunk"] for d in rows)))
