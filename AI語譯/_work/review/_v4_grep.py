# -*- coding: utf-8 -*-
"""Search raw text with context. usage: python _v4_grep.py "pat1,pat2" <file> <out>"""
import sys, os, re
D = os.path.dirname(__file__)
pats = sys.argv[1].split(",")
f = sys.argv[2]
outp = sys.argv[3]
txt = open(f, encoding="utf-8-sig", errors="replace").read().replace("\r\n", "\n")
buf = []
for p in pats:
    for m in re.finditer(p, txt):
        s = max(0, m.start() - 150)
        e = min(len(txt), m.end() + 200)
        buf.append("### [%s] @%d\n%s" % (p, m.start(), txt[s:e].replace("\n", " / ")))
open(os.path.join(D, outp), "w", encoding="utf-8").write("\n\n".join(buf) if buf else "NO MATCH")
print(outp, len(buf))
