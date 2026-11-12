# -*- coding: utf-8 -*-
"""r2 1871-1912 掃描：列每檔 seq→book/chunk/seg、原文/譯文長度、與 out 現行是否相同。"""
import os, sys, io
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import _r2a_lib as L

a, b = int(sys.argv[1]), int(sys.argv[2])
cache = {}
for n in range(a, b + 1):
    recs = L.parse_review(n)
    same = diff = 0
    miss = 0
    for r in recs:
        k = (r['book'], r['chunk'])
        if k not in cache:
            try:
                cache[k] = L.Out(*k)
            except Exception:
                cache[k] = None
        o = cache[k]
        if o is None:
            miss += 1
            continue
        t = o.segs[r['seg'] - 1] if 0 <= r['seg'] - 1 < len(o.segs) else ''
        if t == (r['trans'] or ''):
            same += 1
        else:
            diff += 1
    print('%d: %d segs, same=%d diff=%d miss=%d chunks=%s' % (
        n, len(recs), same, diff, miss,
        ','.join(sorted(set(r['chunk'] for r in recs)))))
