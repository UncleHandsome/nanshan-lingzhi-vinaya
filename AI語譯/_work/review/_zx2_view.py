# -*- coding: utf-8 -*-
"""印出某檔指定 seq 的原文＋現行譯文（全段）。用法: python _zx2_view.py 1048 [1 2 ...]"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _r2a_lib as L

n = int(sys.argv[1])
want = set(int(x) for x in sys.argv[2:])
recs = L.parse_review(n)
outs = {}
for r in recs:
    if want and r['seq'] not in want:
        continue
    k = (r['book'], r['chunk'])
    if k not in outs:
        outs[k] = L.Out(*k)
    cur = outs[k].segs[r['seg'] - 1]
    print('=== %d %s/%s#%d' % (r['seq'], r['book'], r['chunk'], r['seg']))
    print('原: ' + (r['orig'] or '').replace('\n', ''))
    print('譯: ' + cur.replace('\n', '\u23ce'))
    print()
