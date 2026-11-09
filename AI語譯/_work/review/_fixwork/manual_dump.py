# -*- coding: utf-8 -*-
import json, os
W = r"AI語譯/_work/review/_fixwork"
recs = [json.loads(l) for l in open(os.path.join(W, "parsed2.jsonl"), encoding="utf-8")]
manual = [r for r in recs if r["mode"].startswith("manual")]
print(len(manual))
B = 17
for b in range(0, len(manual), B):
    part = manual[b:b+B]
    with open(os.path.join(W, f"m_{b//B:02d}.txt"), "w", encoding="utf-8") as f:
        for r in part:
            f.write(f"=== idx={r['idx']} gid={r['gid']} chunk={r['chunk']} seg={r['seg']} {r['level']}/{r['cls']}\n")
            f.write(f"P: {r['problem']}\n")
            f.write(f"S: {r['suggestion']}\n")
            f.write(f"C: {r['current']}\n\n")
print("batches:", (len(manual)+B-1)//B)
