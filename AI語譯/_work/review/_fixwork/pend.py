# -*- coding: utf-8 -*-
import json, os
W = r"AI語譯/_work/review/_fixwork"
recs = [json.loads(l) for l in open(os.path.join(W, "parsed2.jsonl"), encoding="utf-8")]
by = {r["idx"]: r for r in recs}
# pending fixes for segments whose current contains internal newlines (cannot go into single-line TSV)
PEND = [
    (135, "其一、約定說法四句：", "其一、就言語之法辨四句："),
    (136, "僧已作觀審懷疑是觀想〔犯突吉羅〕", "僧已作觀審懷疑是否成觀〔犯突吉羅〕"),
    (137, "殘害生草木戒中的中間二重", "殘害生草木戒中的二重"),
    (138, "說明並非實際上不適用", "說明並非當前所用之故"),
]
with open(os.path.join(W, "multiline_pending.tsv"), "w", encoding="utf-8", newline="\n") as f:
    for i, old, new in PEND:
        r = by[i]
        n = r["current"].count(old)
        f.write(f"{r['book']}\t{r['chunk']}\t{r['seg']}\t{old}\t{new}\tcount={n}\n")
        assert n == 1, (i, n)
print("ok")
