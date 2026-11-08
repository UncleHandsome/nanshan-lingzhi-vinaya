# -*- coding: utf-8 -*-
import json, os, re
W = r"AI語譯/_work/review/_fixwork"
recs = [json.loads(l) for l in open(os.path.join(W, "parsed.jsonl"), encoding="utf-8")]

with open(os.path.join(W, "auto_diffs.txt"), "w", encoding="utf-8") as f:
    for r in recs:
        if r["mode"] not in ("auto",):
            continue
        f.write(f"### idx={r['idx']} gid={r['gid']} cls={r['cls']}\n")
        for a, b in r["a_ok"]:
            f.write(f"  A[{len(a)}]: {a}\n")
            f.write(f"  B[{len(b)}]: {b}\n")
        f.write("\n")

with open(os.path.join(W, "manual_list.txt"), "w", encoding="utf-8") as f:
    for r in recs:
        if r["mode"] in ("auto", "skip_nosugg"):
            continue
        f.write(f"=== idx={r['idx']} gid={r['gid']} chunk={r['chunk']} seg={r['seg']} {r['level']} {r['cls']} MODE={r['mode']}\n")
        f.write(f"PROBLEM: {r['problem']}\n")
        f.write(f"SUGG: {r['suggestion']}\n")
        if r.get("bad"):
            for t in r["bad"]:
                f.write(f"BAD: {t}\n")
        f.write(f"CURRENT: {r['current']}\n\n")

# quote style check
n_auto_quote = sum(1 for r in recs if r["mode"] == "auto" and any(("『" in b or "』" in b) for a, b in r["a_ok"]))
print("auto with 『』 in B:", n_auto_quote)
print("manual_other idx:", [r["idx"] for r in recs if r["mode"] == "manual_other"])
