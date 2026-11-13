# -*- coding: utf-8 -*-
import os, io, re, sys
ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
X7 = os.path.join(ROOT, "校閱_7K")
OUT = os.path.join(ROOT, "AI語譯", "out")
RESP = os.path.join(ROOT, "batch_qwen", "r7k")

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

nums = list(range(2630, 2655))
files = {}
for n in nums:
    segs = parse(n)
    rp = os.path.join(RESP, "resp_%d.txt" % n)
    rlen = len(rd(rp)) if os.path.exists(rp) else -1
    chunk = segs[0]["chunk"] if segs else "?"
    files.setdefault(chunk, []).append(n)
    print("%d\t%d segs\tchunk=%s\tidx %d-%d\tsrc %d\ttr %d\tresp %d" % (
        n, len(segs), chunk, segs[0]["idx"], segs[-1]["idx"],
        sum(len(s["src"]) for s in segs), sum(len(s["tr"]) for s in segs), rlen))
print("--- files ---")
for c, ns in files.items():
    p = os.path.join(OUT, *c.split("/")) + ".txt"
    raw = rd(p)
    eol = "CRLF" if "\r\n" in raw else "LF"
    idxs = [i for i, l in enumerate(raw.split("\r\n" if eol == "CRLF" else "\n")) if l.strip()]
    print("%s\t%d chunks\t%d-%d\tlines=%d eol=%s" % (c, len(ns), ns[0], ns[-1], len(idxs), eol))
