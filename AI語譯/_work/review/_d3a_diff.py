# -*- coding: utf-8 -*-
import re, os, io, sys
ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
X7 = os.path.join(ROOT, "校閱_7K")
OUT = os.path.join(ROOT, "AI語譯", "out")

def rd(p):
    with io.open(p, "r", encoding="utf-8", newline="") as f:
        return f.read()

def parse_x7(n):
    t = rd(os.path.join(X7, "校閱_%d.txt" % n)).replace("\r\n", "\n")
    segs, cur = [], None
    for ln in t.split("\n"):
        m = re.match(r"^【(\d{4})-(\d{4})】\s*(\S+)#(\d+)\s*$", ln.strip())
        if m:
            cur = {"no": m.group(1) + "-" + m.group(2), "chunk": m.group(3), "idx": int(m.group(4)), "src": "", "tr": ""}
            segs.append(cur); continue
        if cur is not None:
            if ln.startswith("【原文】"): cur["src"] = ln[4:].strip()
            elif ln.startswith("【譯文】"): cur["tr"] = ln[4:].strip()
    return segs

cache = {}
def read_chunk(chunk):
    if chunk in cache: return cache[chunk]
    book, name = chunk.split("/", 1)
    p = os.path.join(OUT, book, name + ".txt")
    raw = rd(p)
    eol = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.split(eol)
    idxs = [i for i, l in enumerate(lines) if l.strip()]
    cache[chunk] = (raw, eol, lines, idxs, p)
    return cache[chunk]

diff = 0; tot = 0
for n in range(1939, 1964):
    for s in parse_x7(n):
        raw, eol, lines, idxs, p = read_chunk(s["chunk"])
        cur = lines[idxs[s["idx"] - 1]].strip()
        tot += 1
        if cur != s["tr"]:
            diff += 1
            print("%s #%d DIFF" % (s["no"], s["idx"]))
print("total %d diff %d" % (tot, diff))
