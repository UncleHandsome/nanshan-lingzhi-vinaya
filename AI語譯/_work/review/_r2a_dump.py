# -*- coding: utf-8 -*-
"""印出某檔所有段：標籤行 + 現行譯文（每段一行）。用法: python _r2a_dump.py 1015"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import _r2a_lib as L

n = int(sys.argv[1])
cache = {}
for r in L.parse_review(n):
    key = (r['book'], r['chunk'])
    if key not in cache:
        cache[key] = L.Out(*key)
    o = cache[key]
    t = o.segs[r['seg'] - 1] if r['seg'] - 1 < len(o.segs) else '<MISSING>'
    print('### %d %s#%d' % (r['seq'], r['chunk'], r['seg']))
    print(t)
