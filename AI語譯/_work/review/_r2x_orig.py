# -*- coding: utf-8 -*-
"""印某檔各 seq 的材料原文。用法: python _r2x_orig.py 1776 [11 12 ...]"""
import os, sys, io
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import _r2a_lib as L

n = int(sys.argv[1])
want = set(int(x) for x in sys.argv[2:]) if len(sys.argv) > 2 else None
for r in L.parse_review(n):
    if want is not None and r['seq'] not in want:
        continue
    print('--- seq%d %s/%s#%d' % (r['seq'], r['book'], r['chunk'], r['seg']))
    print((r['orig'] or '').strip())
