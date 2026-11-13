# -*- coding: utf-8 -*-
import os, io, re, sys
sys.path.insert(0, r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\review")
import _k35
ROOT = _k35.ROOT
BAK = os.path.join(ROOT, "歸檔", "7K卷修正前", "03_業疏")

def rd(p):
    with io.open(p, encoding="utf-8", newline="") as f:
        return f.read()

tot = 0
for n in range(2630, 2655):
    segs = _k35.parse(n)
    per = {}
    for s in segs:
        chunk = s["chunk"]
        if chunk not in per:
            p, raw, eol, L, idxs = _k35.chunk_lines(chunk)
            b = rd(os.path.join(BAK, chunk.split("/")[1] + "_v.txt"))
            eb = "\r\n" if "\r\n" in b else "\n"
            Lb = b.split(eb)
            idxb = [i for i, l in enumerate(Lb) if l.strip()]
            per[chunk] = (L, idxs, Lb, idxb, eol, eb, len(L), len(Lb))
        L, idxs, Lb, idxb, eol, eb, nl, nlb = per[chunk]
        cur = L[idxs[s["idx"] - 1]]
        old = Lb[idxb[s["idx"] - 1]]
        if cur != old:
            print("%d %s#%d changed" % (n, chunk.split("/")[1], s["idx"]))
            tot += 1
    for chunk, (L, idxs, Lb, idxb, eol, eb, nl, nlb) in per.items():
        if nl != nlb:
            print("!! %s line count %d -> %d" % (chunk, nlb, nl))
print("total changed segments:", tot)
