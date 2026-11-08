# -*- coding: utf-8 -*-
import json, os
W = r"AI語譯/_work/review/_fixwork"
recs = [json.loads(l) for l in open(os.path.join(W, "parsed2.jsonl"), encoding="utf-8")]

with open(os.path.join(W, "auto_diff2.txt"), "w", encoding="utf-8") as f:
    for r in recs:
        if r["mode"] != "auto":
            continue
        f.write(f"#{r['idx']} [{r['cls']}]\n")
        for p in r["ops"]:
            ctx0 = r["current"][max(0, p["pos"]-12):p["pos"]]
            ctx1 = r["current"][p["pos"]+len(p["am"]):p["pos"]+len(p["am"])+12]
            f.write(f"  ...{ctx0}【{p['am']}→{p['b']}】{ctx1}...\n")
        f.write("\n")

# manual index with sizes
with open(os.path.join(W, "manual_ids.txt"), "w", encoding="utf-8") as f:
    for r in recs:
        if r["mode"].startswith("manual"):
            f.write(f"{r['idx']}\t{r['cls']}\tlen_cur={len(r['current'])}\tlen_sug={len(r['suggestion'])}\tproblem={r['problem'][:80]}\n")
print("done")
