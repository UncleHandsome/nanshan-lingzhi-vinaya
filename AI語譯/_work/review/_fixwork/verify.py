# -*- coding: utf-8 -*-
import csv, json, os, difflib
W = r"AI語譯/_work/review/_fixwork"
OUT = r"AI語譯/_work/review/fix_re3_g1.tsv"

with open(OUT, encoding="utf-8", newline="") as f:
    rows = list(csv.reader(f, delimiter="\t", quotechar='"'))
print("rows:", len(rows), "fieldcounts:", set(len(r) for r in rows))
print("empty new:", sum(1 for r in rows if not r[3].strip()))
print("tabs in new:", sum(1 for r in rows if "\t" in r[3]))
print("newlines in new:", sum(1 for r in rows if "\n" in r[3]))
keys = [(r[1], r[2]) for r in rows]
print("dup keys:", len(keys) - len(set(keys)))

recs = [json.loads(l) for l in open(os.path.join(W, "parsed2.jsonl"), encoding="utf-8")]
by = {(r["chunk"], r["seg"]): r for r in recs}

issues = []
sizes = []
for r in rows:
    key = (r[1], r[2])
    src = by.get(key)
    if src is None:
        issues.append(("nokey", key)); continue
    cur, new = src["current"].rstrip("\n"), r[3]
    # quote balance
    if new.count("\u300c") != new.count("\u300d"):
        issues.append(("q", src["idx"], new.count("\u300c"), new.count("\u300d")))
    if new.count("\u3014") != new.count("\u3015"):
        issues.append(("brk", src["idx"], new.count("\u3014"), new.count("\u3015")))
    sm = difflib.SequenceMatcher(None, cur, new)
    ratio = sm.ratio()
    sizes.append((round(1 - ratio, 3), src["idx"], len(cur), len(new)))

sizes.sort(reverse=True)
print("largest change ratios (top 15):", sizes[:15])
print("issues:", issues)
with open(os.path.join(W, "ratio.txt"), "w", encoding="utf-8") as f:
    for a, b, c, d in sizes[:25]:
        f.write(f"ratio_change={a} idx={b} curlen={c} newlen={d}\n")
