# -*- coding: utf-8 -*-
"""巡檢 172-206：材料段數、chunk、與現行 out 的 OK/DIFF 統計。"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _7kv_lib as L

IDS = list(range(172, 207))
summary = []
detail = {}
for n in IDS:
    items = L.parse_material(n)
    rec = dict(nnn=n, items=len(items), chunks=[])
    for ch in sorted(set(i["chunk"] for i in items)):
        sub = [i for i in items if i["chunk"] == ch]
        p, b, t, pm = L.chunk_paras(ch)
        same, diff, miss = [], [], []
        for it in sub:
            idx = it["seg"] - 1
            if idx >= len(pm):
                miss.append(it["label"])
                continue
            cur = pm[idx][1].strip()
            (same if cur == it["tr"].strip() else diff).append(it["label"])
        rec["chunks"].append(dict(ch=ch, paras=len(pm), eol=L.eol_of(t), n=len(sub),
                                  same=len(same), diff=len(diff), miss=len(miss)))
        detail.setdefault(ch, dict(paras=len(pm), eol=L.eol_of(t), diff=[], same=[], miss=[]))
        detail[ch]["diff"] += diff
        detail[ch]["same"] += same
        detail[ch]["miss"] += miss
    summary.append(rec)

print("nnn  items chunk            paras eol  n same diff miss")
for r in summary:
    for c in r["chunks"]:
        print("%3d  %5d %-16s %5d %-4s %2d %4d %4d %4d" % (
            r["nnn"], r["items"], c["ch"], c["paras"], c["eol"], c["n"], c["same"], c["diff"], c["miss"]))
tot_items = sum(r["items"] for r in summary)
tot_diff = sum(len(v["diff"]) for v in detail.values())
print("\nfiles=%d items=%d chunks=%d diff_items=%d same_items=%d" % (
    len(summary), tot_items, len(detail), tot_diff,
    sum(len(v["same"]) for v in detail.values())))
print("\n=== 每 chunk DIFF 段 ===")
for ch in sorted(detail):
    v = detail[ch]
    print("%-16s paras=%d diff=%s miss=%s" % (ch, v["paras"], v["diff"], v["miss"]))
json.dump(detail, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "_7kv_detail.json"), "w",
                       encoding="utf-8"), ensure_ascii=False, indent=1)
