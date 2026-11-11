# -*- coding: utf-8 -*-
"""印出某檔各段：材料【原文】 + out 現行譯文。用法: python _r2c_show.py 1491 [6,7,8|all]"""
import os, sys, io
sys.path.insert(0, os.path.dirname(__file__))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import _r2a_lib as L

n = int(sys.argv[1])
only = None
if len(sys.argv) > 2 and sys.argv[2] != 'all':
    only = set(int(x) for x in sys.argv[2].split(','))
cache = {}
for r in L.parse_review(n):
    if only and r['seg'] not in only:
        continue
    key = (r['book'], r['chunk'])
    if key not in cache:
        cache[key] = L.Out(*key)
    o = cache[key]
    cur = o.segs[r['seg'] - 1]
    print('=== %d-%04d %s/%s#%d' % (r['batch'], r['seq'], r['book'], r['chunk'], r['seg']))
    print('[原文] ' + (r['orig'] or ''))
    print('[現行] ' + cur)
    print()
