# -*- coding: utf-8 -*-
"""印出某檔各段現行譯文（可指定段）。用法: python _r2b_seg.py 1335 [1,2,3]"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import _r2a_lib as L

n = int(sys.argv[1])
only = None
if len(sys.argv) > 2:
    only = set(int(x) for x in sys.argv[2].split(','))
cache = {}
for r in L.parse_review(n):
    if only and r['seq'] not in only:
        continue
    key = (r['book'], r['chunk'])
    if key not in cache:
        cache[key] = L.Out(*key)
    o = cache[key]
    cur = o.segs[r['seg'] - 1]
    print('[%d-%04d %s/%s#%d]' % (r['batch'], r['seq'], r['book'], r['chunk'], r['seg']))
    print(cur)
    print()
