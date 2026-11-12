# -*- coding: utf-8 -*-
"""Verify deliverables."""
import os, re, json, sys, io
from collections import Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SU = os.path.join(ROOT, "存疑材料")
BJ = os.path.join(SU, "補判")
TOOLS = os.path.join(BJ, "_tools")

def rd(p):
    with open(p, encoding="utf-8") as f:
        return f.read()

files = sorted(f for f in os.listdir(BJ) if re.match(r"新_補_\d+\.md$", f))
print("new files:", len(files))
all_lab = []
bad = []
for f in files:
    t = rd(os.path.join(BJ, f))
    t = re.sub(r"```text.*?```", "", t, flags=re.S)
    blocks = re.split(r"^### ", t, flags=re.M)[1:]
    n = len(blocks)
    all_lab += [b.split("\n")[0].strip() for b in blocks]
    if not (10 <= n <= 15):
        bad.append((f, n))
    for b in blocks:
        for fld in ("- **段號**", "- **書/chunk#段**", "- **原文**", "- **現行譯文**", "- **疑點**", "- **原檔**"):
            if fld not in b:
                bad.append((f, b.split("\n")[0][:20], "missing " + fld))
        m1 = re.search(r"- \*\*原文\*\*：(.*)", b)
        m2 = re.search(r"- \*\*現行譯文\*\*：(.*)", b)
        if not m1 or len(m1.group(1).strip()) < 8:
            bad.append((f, b.split("\n")[0][:20], "short src"))
        if not m2 or len(m2.group(1).strip()) < 15:
            bad.append((f, b.split("\n")[0][:20], "short tra"))
print("entries:", len(all_lab), "| per-file out of 10..15:", bad[:5])
print("dup labels:", [k for k, v in Counter(all_lab).items() if v > 1][:10])

# overlap with judged + re0 補
judged = set(json.load(open(os.path.join(TOOLS, "n3_final.json"), encoding="utf-8")) and [])
P = json.load(open(os.path.join(TOOLS, "n1_parsed.json"), encoding="utf-8"))
jbase = set(P["judged_base"])
old = set()
for f in os.listdir(BJ):
    if re.match(r"re0_補_\d+\.md$", f):
        old |= set(re.findall(r"^- \*\*段號\*\*：(.+)$", rd(os.path.join(BJ, f)), re.M))
print("overlap with judged:", len(set(all_lab) & jbase))
print("overlap with re0補:", len(set(all_lab) & old))

u = rd(os.path.join(BJ, "新_無法補齊.txt"))
nu = len(re.findall(r"^## ", u, re.M))
print("新_無法補齊 entries:", nu)
print("N (new doubts) =", len(all_lab) + nu)

D = json.load(open(os.path.join(TOOLS, "n4_built.json"), encoding="utf-8"))
print("build stats: resolved", len(D["resolved"]), "unresolved", len(D["unresolved"]))
print("books:", Counter(r["book"] for r in D["resolved"]))
idx = rd(os.path.join(BJ, "index.md"))
print("index mentions 新_補_19:", "新_補_19" in idx, "| 待判:", "待判" in idx)
