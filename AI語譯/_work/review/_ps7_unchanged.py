# -*- coding: utf-8 -*-
"""建 tag→(chunk,seg) 對照；統計 01a-02a 各段是否曾被修改；列出「零修改段」及其 r2 意見塊數。"""
import re, os, glob, json
from collections import defaultdict

BASE = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"

# 1) 材料標籤
tag2seg = {}
for p in glob.glob(os.path.join(BASE, "校閱_10K", "校閱_*.txt")):
    for ln in open(p, encoding="utf-8"):
        m = re.match(r"^【(\d{3}-\d{4})】\s*資持記/(\S+)#(\d+)\s*$", ln.strip())
        if m:
            tag2seg[m.group(1)] = (m.group(2), int(m.group(3)))
print("tags:", len(tag2seg))

# 2) 已改段
changed = set()
for ln in open(os.path.join(BASE, "AI語譯", "_work", "review", "fix_r2_zhichi.tsv"), encoding="utf-8"):
    f = ln.rstrip("\n").split("\t")
    if len(f) >= 3:
        changed.add((f[1], int(f[2])))
for name in ("_r2z2_log.jsonl", "_r2z3_log.jsonl"):
    p = os.path.join(BASE, "AI語譯", "_work", "review", name)
    if not os.path.exists(p):
        continue
    for ln in open(p, encoding="utf-8"):
        try:
            d = json.loads(ln)
        except Exception:
            continue
        changed.add((d.get("chunk", ""), int(d.get("seg", 0))))
print("changed segments:", len(changed))

# 3) 範圍內所有段
covered = []
for p in sorted(glob.glob(os.path.join(BASE, "AI語譯", "out", "資持記", "*.txt"))):
    base = os.path.basename(p)
    if not any(base.startswith(f) for f in ("01a", "01b", "01c", "01d", "01e", "01f", "02a")):
        continue
    chunk = os.path.splitext(base)[0]
    idx = 0
    for ln in open(p, encoding="utf-8").read().split("\n"):
        if ln.strip():
            idx += 1
            covered.append((chunk, idx, ln.strip()))
print("covered segs:", len(covered))
unchanged = [c for c in covered if (c[0], c[1]) not in changed]
print("unchanged segs:", len(unchanged))
for c in unchanged:
    print("  ", c[0].split("_")[0], "#", c[1], c[2][:40])
