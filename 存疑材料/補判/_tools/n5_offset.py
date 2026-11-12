# -*- coding: utf-8 -*-
"""Probe: does 存疑 heading chunk#seg align with TXT_分卷 paragraph index (constant offset)?"""
import os, re, json, sys, io
from collections import Counter, defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SU = os.path.join(ROOT, "存疑材料")
def rd(p):
    with open(p, encoding="utf-8") as f:
        return f.read()
norm = lambda s: re.sub(r"\s+", "", s)

P = json.load(open(os.path.join(SU, "補判", "_tools", "n1_parsed.json"), encoding="utf-8"))
items = P["items"]

def chunk_dir(book):
    if book == "03_業疏":
        return os.path.join(ROOT, "TXT_分卷_標點", book)
    if book == "資持記":
        return os.path.join(ROOT, "TXT_分卷", "資持記_細分")
    return os.path.join(ROOT, "TXT_分卷", book)
def find_file(d, chunk):
    if not os.path.isdir(d): return None
    for f in sorted(os.listdir(d)):
        if f.startswith(chunk) and f.endswith(".txt"):
            return os.path.join(d, f)
    return None
_c = {}
def paras(p):
    if p not in _c:
        _c[p] = [l.strip() for l in rd(p).split("\n") if l.strip()]
    return _c[p]

CHUNK = re.compile(r"([0-9]{2}[a-z]|00_卷首)[_\u4e00-\u9fff]{0,8}\s*(?:#|＃)\s*(\d+)")
ALIAS = {}
for book in ("01_行事鈔", "02_戒疏", "03_業疏", "04_比丘尼鈔", "05_拾毗尼義鈔", "資持記"):
    d = chunk_dir(book)
    if not os.path.isdir(d): continue
    for f in os.listdir(d):
        if f.endswith(".txt"):
            ALIAS[(book, f.split("_")[0])] = f

rows = []
for it in items:
    bk = it.get("book_guess")
    if not bk: continue
    m = CHUNK.search(it["raw"])
    if not m: continue
    chunk, seg = m.group(1), int(m.group(2))
    fn = ALIAS.get((bk, chunk))
    if not fn: continue
    # extract 原文 snippet from body
    mm = re.search(r"原文[^\n：:]*[：:]\s*`([^`]+)`", it["body"])
    if not mm:
        mm = re.search(r"原文[^\n：:]*[：:]\s*([^\n]{6,})", it["body"])
    if not mm: continue
    snip = norm(mm.group(1))[:20]
    if len(snip) < 8: continue
    ps = paras(os.path.join(chunk_dir(bk), fn))
    joined, offs, cur = norm("".join(ps)), [], 0
    for p in ps:
        offs.append(cur); cur += len(norm(p))
    pos = joined.find(snip)
    if pos < 0: continue
    a = max(i for i, o in enumerate(offs) if o <= pos)
    rows.append((bk, chunk, seg, a + 1, (a + 1) - seg, snip[:12]))

print("pairs tested:", len(rows))
by = defaultdict(list)
for bk, chunk, seg, para, delta, snip in rows:
    by[(bk, chunk)].append(delta)
for k, v in sorted(by.items()):
    print(f"  {k[0]}/{k[1]}: n={len(v)} deltas={Counter(v).most_common(4)}")
print("\nsample rows:")
for r in rows[:12]:
    print("  ", r)
