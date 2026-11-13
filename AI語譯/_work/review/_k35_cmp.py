# -*- coding: utf-8 -*-
import os, io, re
ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
X7 = os.path.join(ROOT, "校閱_7K"); OUT = os.path.join(ROOT, "AI語譯", "out")

def rd(p):
    with io.open(p, encoding="utf-8", newline="") as f:
        return f.read()

def parse(n):
    t = rd(os.path.join(X7, "校閱_%d.txt" % n)).replace("\r\n", "\n")
    segs, cur = [], None
    for ln in t.split("\n"):
        m = re.match(r"^【(\d{4}-\d{4})】\s*(\S+)#(\d+)\s*$", ln.strip())
        if m:
            cur = {"no": m.group(1), "chunk": m.group(2), "idx": int(m.group(3)), "src": "", "tr": ""}
            segs.append(cur); continue
        if cur is not None:
            if ln.startswith("【原文】"): cur["src"] = ln[4:].strip()
            elif ln.startswith("【譯文】"): cur["tr"] = ln[4:].strip()
    return segs

cache = {}
def lines_of(chunk):
    if chunk not in cache:
        raw = rd(os.path.join(OUT, *chunk.split("/")) + ".txt")
        eol = "\r\n" if "\r\n" in raw else "\n"
        L = raw.split(eol)
        cache[chunk] = (raw, eol, L, [i for i, l in enumerate(L) if l.strip()])
    return cache[chunk]

for n in range(2630, 2655):
    segs = parse(n)
    diffs = 0
    for s in segs:
        raw, eol, L, idxs = lines_of(s["chunk"])
        c = L[idxs[s["idx"] - 1]].strip()
        if c != s["tr"]:
            diffs += 1
    print(n, "segs", len(segs), "diff_vs_material", diffs)
