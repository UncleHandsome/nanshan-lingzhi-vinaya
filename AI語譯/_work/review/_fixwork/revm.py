# -*- coding: utf-8 -*-
import csv, json, os
W = r"AI語譯/_work/review/_fixwork"
OUT = r"AI語譯/_work/review/fix_re3_g1.tsv"
rows = list(csv.reader(open(OUT, encoding="utf-8", newline=""), delimiter="\t", quotechar='"'))
recs = [json.loads(l) for l in open(os.path.join(W, "parsed2.jsonl"), encoding="utf-8")]
cur = {}
for r in recs:
    cur.setdefault((r["chunk"], r["seg"]), r["current"].rstrip("\n"))
byn = {(r[0], r[1], r[2]): r[3] for r in rows}
with open(os.path.join(W, "review_merged.txt"), "w", encoding="utf-8") as f:
    for k in [("07c_中一下", "12"), ("09b_中三上", "49"), ("12c_中四下", "2"),
              ("11d_中四上", "1"), ("08d_中二", "31"), ("09c_中三上", "19"),
              ("10b_中三下", "7"), ("11a_中四上", "36"), ("12a_中四下", "55"),
              ("12a_中四下", "63")]:
        f.write(f"##### {k}\nOLD: {cur[k]}\nNEW: {byn[('資持記', k[0], k[1])]}\n\n")
print("ok")
