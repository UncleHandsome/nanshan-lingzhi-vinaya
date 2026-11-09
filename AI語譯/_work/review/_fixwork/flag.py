# -*- coding: utf-8 -*-
import json, os
W = r"AI語譯/_work/review/_fixwork"
recs = [json.loads(l) for l in open(os.path.join(W, "parsed2.jsonl"), encoding="utf-8")]
with open(os.path.join(W, "flag_auto.txt"), "w", encoding="utf-8") as f:
    for r in recs:
        if r["mode"] != "auto":
            continue
        for p in r["ops"]:
            b = p["b"]
            marks = [m for m in ["\u2026\u2026", "（或", "或刪", "（應", "？", "！？"] if m in b]
            if marks:
                f.write(f"#{r['idx']} marks={marks}\n  B: {b}\n")
print("ok")
