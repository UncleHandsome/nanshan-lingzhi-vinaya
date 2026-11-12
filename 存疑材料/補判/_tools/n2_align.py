# -*- coding: utf-8 -*-
"""Probe alignment: 校閱 【原文】 vs TXT_分卷 para[seg-1]; 校閱 【譯文】 vs out para[seg-1]."""
import os, re, json, sys, io, difflib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SU = os.path.join(ROOT, "存疑材料")

def rd(p):
    with open(p, encoding="utf-8") as f:
        return f.read()

HDR = re.compile(r"^【(\d{3,4}-\d{4})】 *(.+)$", re.M)
SRC = re.compile(r"^【原文】(.*)$", re.M)
TRA = re.compile(r"^【譯文】(.*)$", re.M)

norm = lambda s: re.sub(r"\s+", "", s)
def sim(a, b):
    a, b = norm(a), norm(b)
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(None, a, b).ratio()

def chunk_dir(book):
    base = "TXT_分卷_標點" if book == "03_業疏" else "TXT_分卷"
    return os.path.join(ROOT, base, book)

def find_file(d, chunk):
    if not os.path.isdir(d):
        return None
    cand = sorted(f for f in os.listdir(d) if f.startswith(chunk) and f.endswith(".txt"))
    return os.path.join(d, cand[0]) if cand else None

cache = {}
def paras(p):
    if p not in cache:
        cache[p] = [l.strip() for l in rd(p).split("\n") if l.strip()]
    return cache[p]

# parse 校閱 files: key -> (loc, src, tra)
recs = {}
files = []
for sub in ("校閱_10K",):
    d = os.path.join(ROOT, sub)
    for fn in sorted(os.listdir(d))[:40]:
        files.append(os.path.join(d, fn))
for p in files:
    t = rd(p)
    ms = list(HDR.finditer(t))
    for i, m in enumerate(ms):
        end = ms[i + 1].start() if i + 1 < len(ms) else len(t)
        blk = t[m.end():end]
        sm, tm = SRC.search(blk), TRA.search(blk)
        recs[m.group(1)] = (m.group(2).strip(),
                            sm.group(1).strip() if sm else "",
                            tm.group(1).strip() if tm else "")

print("recs", len(recs))
res = {"src_ok": 0, "src_bad": 0, "tra_ok": 0, "tra_bad": 0}
bad = []
for key, (loc, src, tra) in sorted(recs.items()):
    mm = re.match(r"^(.+?)/([^#]+)#(\d+)", loc)
    if not mm:
        continue
    book, chunk, seg = mm.group(1), mm.group(2), int(mm.group(3))
    sp = find_file(chunk_dir(book), chunk)
    op = find_file(os.path.join(ROOT, "AI語譯", "out", book), chunk)
    if not sp or not op:
        bad.append((key, book, chunk, seg, "nofile", bool(sp), bool(op)))
        continue
    tps, ops = paras(sp), paras(op)
    if seg - 1 >= len(tps) or seg - 1 >= len(ops):
        bad.append((key, book, chunk, seg, "oor", len(tps), len(ops)))
        continue
    s1, s2 = sim(src, tps[seg - 1]), sim(tra, ops[seg - 1])
    res["src_ok" if s1 > 0.8 else "src_bad"] += 1
    res["tra_ok" if s2 > 0.8 else "tra_bad"] += 1
    if s1 <= 0.8 or s2 <= 0.8:
        bad.append((key, book, chunk, seg, round(s1, 2), round(s2, 2)))

print(res)
print("bad", len(bad))
for b in bad[:25]:
    print("  ", b)

# print one full example
k = "003-0001"
loc, src, tra = recs[k]
mm = re.match(r"^(.+?)/([^#]+)#(\d+)", loc)
book, chunk, seg = mm.group(1), mm.group(2), int(mm.group(3))
tps = paras(find_file(chunk_dir(book), chunk))
ops = paras(find_file(os.path.join(ROOT, "AI語譯", "out", book), chunk))
print("\n=== key", k, loc)
print("SRC 校閱:", src[:90])
print("SRC txt :", tps[seg - 1][:90])
print("TRA 校閱:", tra[:90])
print("TRA out :", ops[seg - 1][:90])
print("\n出處 chunk file:", os.path.basename(find_file(chunk_dir(book), chunk)))
print("out  para count:", len(ops), " txt para count:", len(tps))
