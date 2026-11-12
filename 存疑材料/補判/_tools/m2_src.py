# -*- coding: utf-8 -*-
import json, os, sys
rows = json.load(open(os.path.join(os.path.dirname(__file__), "m2_rows.json"), encoding="utf-8"))
byid = {r["id"]: r for r in rows}
# material 原文 lives in m1? re-parse materials for 原文
import re
MAT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
def rd(p):
    with open(p, encoding="utf-8-sig") as f:
        return f.read().replace("\r\n", "\n")
MAP = {}
for i in range(1, 20):
    txt = rd(os.path.join(MAT, "新_補_%02d.md" % i))
    for b in re.split(r"^###\s+", txt, flags=re.M)[1:]:
        lines = b.split("\n"); seg = lines[0].strip(); d = {}
        for ln in lines:
            m = re.match(r"^-\s+\*\*(.+?)\*\*[：:]\s*(.*)$", ln.strip())
            if m: d[m.group(1)] = m.group(2).strip()
        if "書/chunk#段" in d: MAP[seg] = d
txt = rd(os.path.join(MAT, "末_補_01.md"))
for b in re.split(r"^###\s+", txt, flags=re.M)[1:]:
    lines = b.split("\n"); seg = lines[0].strip(); d = {}
    for ln in lines:
        m = re.match(r"^-\s+\*\*(.+?)\*\*[：:]\s*(.*)$", ln.strip())
        if m: d[m.group(1)] = m.group(2).strip()
    if "書/chunk#段" in d: MAP[seg] = d

for k in sys.argv[1:]:
    r = byid[k]
    print("=" * 70)
    print(k, "| 原文:", MAP[k].get("原文", ""))
    print("| 疑點:", MAP[k].get("疑點", ""))
