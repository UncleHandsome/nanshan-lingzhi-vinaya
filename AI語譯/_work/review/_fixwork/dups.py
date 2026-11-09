# -*- coding: utf-8 -*-
import json, os
from collections import Counter
W = r"AI語譯/_work/review/_fixwork"
recs = [json.loads(l) for l in open(os.path.join(W, "parsed2.jsonl"), encoding="utf-8")]
c = Counter((r["chunk"], r["seg"]) for r in recs)
dups = [k for k, v in c.items() if v > 1]
with open(os.path.join(W, "dups.txt"), "w", encoding="utf-8") as f:
    for k in dups:
        f.write(f"KEY {k}\n")
        for r in recs:
            if (r["chunk"], r["seg"]) == k:
                f.write(f"  idx={r['idx']} gid={r['gid']} mode={r['mode']} curlen={len(r['current'])} cur={r['current'][:70]}\n")
        f.write("\n")
print(len(dups))
