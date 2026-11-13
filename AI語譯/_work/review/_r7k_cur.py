# -*- coding: utf-8 -*-
"""印現行譯文（只印指定段，不印原文/材料），供改後複讀。用法: python _r7k_cur.py 1385-0002 ..."""
import sys, os, io

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _r7k_z02 as Z

for no in sys.argv[1:]:
    for n in range(Z.LO, Z.HI + 1):
        segs = Z.parse_x7(n)
        hit = [s for s in segs if s["no"] == no]
        if hit:
            s = hit[0]
            raw, eol, lines, idxs, p = Z.read_chunk(s["chunk"])
            print("%s #%d %s" % (no, s["idx"], s["chunk"]))
            print(lines[idxs[s["idx"] - 1]].strip())
            print()
            break
