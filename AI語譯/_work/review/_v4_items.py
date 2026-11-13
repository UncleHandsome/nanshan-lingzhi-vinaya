# -*- coding: utf-8 -*-
"""Count reviewer opinion items per resp file (mechanical proxy)."""
import os, re, json
ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
R7K = os.path.join(ROOT, "batch_qwen", "r7k")
D = os.path.dirname(__file__)

num_re = re.compile(r"^\s{0,3}\d+[.、]\s*\S")
bul_re = re.compile(r"^\s{0,3}[-*]\s+\S")
tab_re = re.compile(r"^\s*\|[^|]")

rows = {}
for f in range(258, 293):
    p = os.path.join(R7K, "resp_%d.txt" % f)
    if not os.path.exists(p):
        continue
    items = 0
    for ln in open(p, encoding="utf-8-sig", errors="replace").read().splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith("|") and not re.match(r"^\|[\s:\-|]+\|?$", s):
            # table data row (skip header row if next line is separator — close enough)
            items += 1
            continue
        if num_re.match(ln) or bul_re.match(ln):
            items += 1
    rows[f] = items
json.dump(rows, open(os.path.join(D, "_v4_items.json"), "w", encoding="utf-8"), ensure_ascii=False)
print(json.dumps(rows, ensure_ascii=False))
print("sum", sum(rows.values()))
