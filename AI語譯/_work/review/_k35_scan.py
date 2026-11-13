# -*- coding: utf-8 -*-
import os, io, re, sys
sys.path.insert(0, r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\review")
import _k35
ROOT = _k35.ROOT
BAK = os.path.join(ROOT, "歸檔", "7K卷修正前", "03_業疏")

def rd(p):
    with io.open(p, encoding="utf-8", newline="") as f:
        return f.read()

bad = 0
for n in range(2630, 2655):
    segs = _k35.parse(n)
    cache = {}
    for s in segs:
        chunk = s["chunk"]
        if chunk not in cache:
            p, raw, eol, L, idxs = _k35.chunk_lines(chunk)
            b = rd(os.path.join(BAK, chunk.split("/")[1] + "_v.txt"))
            eb = "\r\n" if "\r\n" in b else "\n"
            Lb = b.split(eb)
            idxb = [i for i, l in enumerate(Lb) if l.strip()]
            cache[chunk] = (raw, L, idxs, Lb, idxb)
        raw, L, idxs, Lb, idxb = cache[chunk]
        cur = L[idxs[s["idx"] - 1]]
        old = Lb[idxb[s["idx"] - 1]]
        # checks
        for pat, msg in [(r"，，", "double comma"), (r"。。", "double period"), (r"的的", "的的"),
                         (r"了了", "了了"), (r"（（）", "paren"), (r"\s{2,}", "spaces")]:
            if re.search(pat, cur):
                print("!! %d #%d %s: %s" % (n, s["idx"], msg, cur[:60])); bad += 1
        if cur.count("「") != cur.count("」"):
            print("!! %d #%d quote mismatch: %d/%d" % (n, s["idx"], cur.count("「"), cur.count("」"))); bad += 1
        if cur.count("（") != cur.count("）"):
            print("!! %d #%d paren mismatch: %d/%d" % (n, s["idx"], cur.count("（"), cur.count("）"))); bad += 1
        if "None" in cur or "{" in cur:
            print("!! %d #%d artifact" % (n, s["idx"])); bad += 1
        if abs(len(cur) - len(old)) > 0.35 * len(old):
            print("!! %d #%d big length change %d -> %d" % (n, s["idx"], len(old), len(cur))); bad += 1
print("issues:", bad)
