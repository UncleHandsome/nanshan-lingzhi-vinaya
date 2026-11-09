# -*- coding: utf-8 -*-
import csv, json, os
W = r"AI語譯/_work/review/_fixwork"
OUT = r"AI語譯/_work/review/fix_re3_g1.tsv"
rows = list(csv.reader(open(OUT, encoding="utf-8", newline=""), delimiter="\t", quotechar='"'))
recs = [json.loads(l) for l in open(os.path.join(W, "parsed2.jsonl"), encoding="utf-8")]
cur = {}
for r in recs:
    cur.setdefault((r["chunk"], r["seg"]), r["current"].rstrip("\n"))
byid = {r["idx"]: r for r in recs}
byn = {(r[1], r[2]): r[3] for r in rows}
pick = [7, 61, 105, 122, 123, 126, 178, 221, 8, 102, 143, 177, 34, 67, 66]
with open(os.path.join(W, "spot.txt"), "w", encoding="utf-8") as f:
    for i in pick:
        r = byid[i]
        k = (r["chunk"], r["seg"])
        if k not in byn:
            f.write(f"#{i} {k} NOT-IN-OUTPUT (skipped)\n\n"); continue
        f.write(f"##### idx={i} {k}\nCUR: {cur[k]}\nNEW: {byn[k]}\n\n")

# rows where nothing changed
same = [r for r in rows if r[3] == cur.get((r[1], r[2]))]
print("unchanged rows:", [(r[1], r[2]) for r in same])
print("count:", len(same))
