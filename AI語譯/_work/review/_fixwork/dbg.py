# -*- coding: utf-8 -*-
import json, os
W = r"AI語譯/_work/review/_fixwork"
recs = [json.loads(l) for l in open(os.path.join(W, "parsed.jsonl"), encoding="utf-8")]
targets = [14,19,36,83,121,142,144,146,152,168,170,171,183,185,187,190,204,205,206,222,227,8,102,122,123,126,129,181]
by = {r["idx"]: r for r in recs}
with open(os.path.join(W, "debug1.txt"), "w", encoding="utf-8") as f:
    for i in targets:
        r = by[i]
        f.write(f"=== {i} mode={r['mode']} nops={r['nops']}\n")
        f.write(f"SUGG: {r['suggestion']}\n")
        f.write(f"BAD: {r.get('bad')}\n")
        f.write(f"CUR: {r['current'][:300]}\n\n")
print("ok")
