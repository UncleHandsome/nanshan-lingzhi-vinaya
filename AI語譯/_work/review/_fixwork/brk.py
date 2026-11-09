# -*- coding: utf-8 -*-
import json, os
W = r"AI語譯/_work/review/_fixwork"
recs = [json.loads(l) for l in open(os.path.join(W, "parsed2.jsonl"), encoding="utf-8")]
by = {r["idx"]: r for r in recs}
with open(os.path.join(W, "brk.txt"), "w", encoding="utf-8") as f:
    for i in (52, 65, 107, 221, 18, 22):
        r = by[i]
        cur = r["current"]
        f.write(f"#{i} mode={r['mode']} cur open={cur.count(chr(0x300c))} close={cur.count(chr(0x300d))}\n")
        f.write(f"  CUR: {cur}\n")
        f.write(f"  SUG: {r['suggestion']}\n")
        f.write(f"  PROB: {r['problem']}\n\n")
print("ok")
