# -*- coding: utf-8 -*-
"""Survey 2761-2778: segment counts, chunk mapping, material-vs-out diffs."""
import os, re, io, sys

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
X7 = os.path.join(ROOT, "校閱_7K")
OUT = os.path.join(ROOT, "AI語譯", "out")


def rd(p):
    with io.open(p, "r", encoding="utf-8", newline="") as f:
        return f.read()


def parse_x7(nnn):
    p = os.path.join(X7, "校閱_%s.txt" % nnn)
    lines = rd(p).replace("\r\n", "\n").split("\n")
    segs, cur = [], None
    for ln in lines:
        m = re.match(r"^【(\d{3,4}-\d{4})】\s*(\S+)#(\d+)\s*$", ln.strip())
        if m:
            cur = {"no": m.group(1), "chunk": m.group(2), "idx": int(m.group(3)), "src": "", "tr": ""}
            segs.append(cur)
            continue
        if cur is not None:
            if ln.startswith("【原文】"):
                cur["src"] = ln[4:].strip()
            elif ln.startswith("【譯文】"):
                cur["tr"] = ln[4:].strip()
    return segs


_cache = {}
def read_chunk(chunk):
    if chunk in _cache:
        return _cache[chunk]
    book, name = chunk.split("/", 1)
    p = os.path.join(OUT, book, name + ".txt")
    raw = rd(p)
    eol = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.split(eol)
    idxs = [i for i, l in enumerate(lines) if l.strip()]
    _cache[chunk] = (raw, eol, lines, idxs, p)
    return _cache[chunk]


for n in range(2761, 2779):
    segs = parse_x7(n)
    chunks = {}
    for s in segs:
        chunks.setdefault(s["chunk"], []).append(s["idx"])
    ne = 0
    for s in segs:
        raw, eol, lines, idxs, p = read_chunk(s["chunk"])
        if lines[idxs[s["idx"] - 1]].strip() != s["tr"]:
            ne += 1
    print("%s\t%d段\t%s\tdiff=%d" % (n, len(segs), "; ".join("%s#%d-%d" % (c, min(v), max(v)) for c, v in chunks.items()), ne))
