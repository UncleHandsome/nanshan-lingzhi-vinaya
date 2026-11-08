# -*- coding: utf-8 -*-
import json, collections
BASE = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\review"
recs = json.load(open(BASE + r"\_qc_rows.json", encoding="utf-8"))
c = collections.Counter((r["book"], r["chunk"], r["seg"]) for r in recs)
dups = [k for k, v in c.items() if v > 1]
g = collections.Counter(r["gid"] for r in recs)
print("dup keys", dups, "dup gid", [k for k, v in g.items() if v > 1])
lines = open(BASE + r"\fix_qc.tsv", encoding="utf-8").read().split("\n")
lines = [l for l in lines if l]
assert len(lines) == 68
keys = set()
for l in lines:
    parts = l.split("\t")
    assert len(parts) == 4, parts
    keys.add((parts[0], parts[1], parts[2]))
print("unique keys", len(keys), "first", lines[0].split("\t")[:3], "last", lines[-1].split("\t")[:3])
print("all books", collections.Counter(l.split("\t")[0] for l in lines))
