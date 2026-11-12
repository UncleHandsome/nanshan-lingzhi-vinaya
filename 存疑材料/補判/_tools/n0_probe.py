# -*- coding: utf-8 -*-
"""Probe: build 段號 index from 校閱_10K / 校閱_20K, verify alignment against
TXT_分卷 paragraphs and AI語譯/out paragraphs."""
import os, re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUT = os.path.join(ROOT, "存疑材料", "補判", "_tools")

HDR = re.compile(r"^【(\d{3,4}-\d{4})】(.+)$")
def rd(p):
    with open(p, encoding="utf-8") as f:
        return f.read()

idx = {}   # key -> dict(book, chunk, seg)
dups = []
for sub in ("校閱_10K", "校閱_20K", "校閱_40K"):
    d = os.path.join(ROOT, sub)
    if not os.path.isdir(d):
        continue
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".txt"):
            continue
        t = rd(os.path.join(d, fn))
        for m in HDR.finditer(t):
            key, loc = m.group(1), m.group(2).strip()
            mm = re.match(r"^(.+?)/([^#]+)#(\d+)$", loc)
            if not mm:
                continue
            book, chunk, seg = mm.group(1), mm.group(2), int(mm.group(3))
            rec = {"book": book, "chunk": chunk, "seg": seg, "src": sub, "file": fn}
            if key in idx and (idx[key]["book"], idx[key]["chunk"], idx[key]["seg"]) != (book, chunk, seg):
                dups.append((key, idx[key], rec))
            idx.setdefault(key, rec)

print("segments indexed:", len(idx))
print("dups (conflicting):", len(dups))
for k, a, b in dups[:10]:
    print("  ", k, a["book"], a["chunk"], a["seg"], "|", b["book"], b["chunk"], b["seg"])

# distribution by book
from collections import Counter
print(Counter(v["book"] for v in idx.values()))

# ---- check paragraph alignment for TXT_分卷 and out ----
cache_txt, cache_out = {}, {}
def paras(p):
    if p not in cache_txt:
        cache_txt[p] = [l.strip() for l in rd(p).split("\n") if l.strip()]
    return cache_txt[p]

def outparas(p):
    if p not in cache_out:
        cache_out[p] = [l.strip() for l in rd(p).split("\n") if l.strip()]
    return cache_out[p]

def srcpath(book, chunk):
    base = "TXT_分卷_標點" if book == "03_業疏" else "TXT_分卷"
    d = os.path.join(ROOT, base, book)
    if not os.path.isdir(d):
        return None
    cand = sorted(f for f in os.listdir(d) if f.startswith(chunk) and f.endswith(".txt"))
    return os.path.join(d, cand[0]) if cand else None

def outpath(book, chunk):
    d = os.path.join(ROOT, "AI語譯", "out", book)
    if not os.path.isdir(d):
        return None
    cand = sorted(f for f in os.listdir(d) if f.startswith(chunk) and f.endswith(".txt"))
    return os.path.join(d, cand[0]) if cand else None

def norm(s):
    return re.sub(r"\s+", "", s)

ok = miss_txt = miss_out = 0
bad_txt = []
sample = sorted(idx.items())[:4000]
for k, v in sample:
    sp = srcpath(v["book"], v["chunk"])
    op = outpath(v["book"], v["chunk"])
    if not sp:
        miss_txt += 1
        continue
    if not op:
        miss_out += 1
        continue
    tps, ops = paras(sp), outparas(op)
    if v["seg"] - 1 >= len(tps) or v["seg"] - 1 >= len(ops):
        bad_txt.append((k, v["book"], v["chunk"], v["seg"], len(tps), len(ops)))
        continue
    ok += 1

print("checked", len(sample), "ok", ok, "no src file", miss_txt, "no out file", miss_out,
      "seg out of range", len(bad_txt))
for b in bad_txt[:10]:
    print("  OOR", b)

json.dump({k: v for k, v in idx.items()}, open(os.path.join(OUT, "seg_index.json"), "w", encoding="utf-8"),
          ensure_ascii=False)
print("wrote seg_index.json")
