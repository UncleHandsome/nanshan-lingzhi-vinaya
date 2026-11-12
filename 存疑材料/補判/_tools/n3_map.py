# -*- coding: utf-8 -*-
"""Map every 校閱 seg to its TXT_分卷 paragraph span, per chunk."""
import os, re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SU = os.path.join(ROOT, "存疑材料")
TOOLS = os.path.join(SU, "補判", "_tools")
def rd(p):
    with open(p, encoding="utf-8") as f: return f.read()
norm = lambda s: re.sub(r"\s+", "", s)

HDR = re.compile(r"^【(\d{3,4}-\d{4})】 *(.+)$", re.M)
SRC = re.compile(r"^【原文】(.*)$", re.M)
segs = {}
for sub in ("校閱_10K",):
    d = os.path.join(ROOT, sub)
    for fn in sorted(os.listdir(d)):
        t = rd(os.path.join(d, fn))
        ms = list(HDR.finditer(t))
        for i, m in enumerate(ms):
            end = ms[i+1].start() if i+1 < len(ms) else len(t)
            sm = SRC.search(t[m.end():end])
            mm = re.match(r"^(.+?)/([^#]+)#(\d+)", m.group(2).strip())
            if sm and mm:
                segs.setdefault((mm.group(1), mm.group(2)), {})[int(mm.group(3))] = (
                    m.group(1), sm.group(1).strip())

print("chunks", len(segs), "segs", sum(len(v) for v in segs.values()))

def chunk_dir(book):
    return os.path.join(ROOT, "TXT_分卷_標點" if book == "03_業疏" else "TXT_分卷", book)
def find_file(d, chunk):
    if not os.path.isdir(d): return None
    c = sorted(f for f in os.listdir(d) if f.startswith(chunk) and f.endswith(".txt"))
    return os.path.join(d, c[0]) if c else None

report = []
for (book, chunk), d in sorted(segs.items()):
    p = find_file(chunk_dir(book), chunk)
    if not p:
        report.append((book, chunk, "NOFILE", 0, 0, 0))
        continue
    paras = [l.strip() for l in rd(p).split("\n") if l.strip()]
    joined = norm("".join(paras))
    # offsets of each para start in joined stream
    offs, cur = [], 0
    for para in paras:
        offs.append(cur); cur += len(norm(para))
    exact = prefix = miss = 0
    for seg in sorted(d):
        key, src = d[seg]
        ns = norm(src)
        if not ns:
            miss += 1; continue
        pos = joined.find(ns)
        if pos >= 0:
            exact += 1
        elif joined.find(ns[:15]) >= 0:
            prefix += 1
        else:
            miss += 1
    report.append((book, chunk, "ok", exact, prefix, miss))

bad = [r for r in report if r[2] != "ok"]
print("chunks failed to open:", len(bad))
for b in bad[:10]: print("  ", b)
tot = [0, 0, 0]
for r in report:
    if r[2] == "ok":
        tot[0] += r[3]; tot[1] += r[4]; tot[2] += r[5]
print("exact", tot[0], "prefix", tot[1], "miss", tot[2], "of", sum(tot))
worst = sorted([r for r in report if r[2] == "ok" and r[5] > 0], key=lambda r: -r[5])
print("chunks with misses:", len(worst))
for w in worst[:12]: print("  ", w)
