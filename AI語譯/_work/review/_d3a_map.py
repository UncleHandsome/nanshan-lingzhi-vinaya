# -*- coding: utf-8 -*-
import re, os, io, sys
ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
X7 = os.path.join(ROOT, "校閱_7K")
for n in range(1939, 1964):
    p = os.path.join(X7, "校閱_%d.txt" % n)
    t = io.open(p, encoding="utf-8").read()
    tags = re.findall(r"^【(\d{4})-(\d{4})】(\S+)#(\d+)$", t, re.M)
    chunks = []
    for g in tags:
        c = g[2] + "#" + g[3]
        if not chunks or chunks[-1].split("-")[0].split("#")[0] != g[2]:
            chunks.append(c + "-" + g[3])
        else:
            chunks[-1] = chunks[-1].split("-")[0] + "-" + g[3]
    print("%d\t%d\t%s\t%s" % (n, len(tags), tags[0][2] + "#" + tags[0][3], tags[-1][2] + "#" + tags[-1][3]))
