# -*- coding: utf-8 -*-
import json, os
W = r"AI語譯/_work/review/_fixwork"
recs = [json.loads(l) for l in open(os.path.join(W, "parsed2.jsonl"), encoding="utf-8")]
by = {r["idx"]: r for r in recs}
with open(os.path.join(W, "nl_dump.txt"), "w", encoding="utf-8") as f:
    for i in [135,136,137,138,139,140,221]:
        r = by[i]
        f.write(f"=== idx={i} gid={r['gid']} chunk={r['chunk']} seg={r['seg']} conf={r['conf']} mode={r['mode']}\n")
        f.write(f"PROBLEM: {r['problem']}\nSUGG: {r['suggestion']}\n")
        f.write(f"CUR: {r['current']!r}\n")
        f.write(f"NEW: {r['new']!r}\n\n")
print("ok")
