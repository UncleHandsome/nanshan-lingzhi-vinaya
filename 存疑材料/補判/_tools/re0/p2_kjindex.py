# -*- coding: utf-8 -*-
"""Build ID -> (book, chunk, seg, src, tr) index from 校閱_10K files."""
import os, re, json, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
K = os.path.join(ROOT, "校閱_10K")

def rd(p):
    with open(p, encoding="utf-8") as f:
        return f.read()

# collect needed numbers from a list of ids
ids = [l.strip() for l in open(os.path.join(ROOT, "存疑材料", "補判", "_tools", "ids.txt"), encoding="utf-8") if l.strip()]
nums = sorted({re.match(r"(\d+)", i).group(1) for i in ids if re.match(r"(\d+)", i)})
print("nums", len(nums))

def parse_file(p):
    t = rd(p)
    # split on 【ID】 lines
    parts = re.split(r"^【(\d{3,4}-\d{4})】(.*)$", t, flags=re.M)
    out = []
    for i in range(1, len(parts) - 1, 3):
        code, label = parts[i], parts[i + 1].strip()
        body = parts[i + 2]
        m1 = re.search(r"【原文】(.*?)(?=\n【譯文】|\Z)", body, re.S)
        m2 = re.search(r"【譯文】(.*?)(?=\n【|\Z)", body, re.S)
        out.append({"code": code, "label": label,
                    "src": (m1.group(1).strip() if m1 else ""),
                    "tr": (m2.group(1).strip() if m2 else "")})
    return out

idx = {}
for n in nums:
    p = os.path.join(K, f"校閱_{n}.txt")
    if not os.path.exists(p):
        continue
    for it in parse_file(p):
        idx.setdefault(it["code"], it)

print("indexed codes", len(idx))
json.dump(idx, open(os.path.join(ROOT, "存疑材料", "補判", "_tools", "kj_index.json"), "w", encoding="utf-8"),
          ensure_ascii=False)
missing = [i for i in ids if i not in idx]
print("missing", len(missing))
open(os.path.join(ROOT, "存疑材料", "補判", "_tools", "kj_missing.txt"), "w", encoding="utf-8").write("\n".join(missing))
