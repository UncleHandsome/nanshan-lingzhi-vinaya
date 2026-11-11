# -*- coding: utf-8 -*-
import re, os, glob, sys

BASE = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUT = os.path.join(BASE, "AI語譯", "out", "資持記")
FILES = ["01a", "01b", "01c", "01d", "01e", "01f", "02a"]

paras = []
for p in sorted(glob.glob(os.path.join(OUT, "*.txt"))):
    base = os.path.basename(p)
    if not any(base.startswith(f) for f in FILES):
        continue
    chunk = os.path.splitext(base)[0]
    idx = 0
    for ln in open(p, encoding="utf-8").read().split("\n"):
        if ln.strip():
            idx += 1
            paras.append((chunk, idx, ln.strip()))

pats = sys.argv[1:]
for pat in pats:
    found = False
    for chunk, idx, t in paras:
        if pat in t:
            found = True
            i = t.index(pat)
            s = max(0, i-40); e = min(len(t), i+len(pat)+40)
            print("【%s】%s#%d  …%s…" % (pat, chunk.split("_")[0], idx, t[s:e]))
    if not found:
        print("【%s】—無—" % pat)
