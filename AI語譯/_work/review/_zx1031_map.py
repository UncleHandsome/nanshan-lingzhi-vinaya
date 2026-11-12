# -*- coding: utf-8 -*-
import os, sys, collections
sys.path.insert(0, os.path.dirname(__file__))
import _r2a_lib as L
rows = []
for n in range(1031, 1181):
    p = os.path.join(L.REV, '校閱_%d.txt' % n)
    if not os.path.exists(p):
        print(n, 'MATERIAL MISSING'); continue
    recs = L.parse_review(n)
    if not recs:
        print(n, 'NO SEGS'); continue
    ch = collections.OrderedDict()
    for r in recs:
        ch.setdefault((r['book'], r['chunk']), []).append(r['seg'])
    s = '; '.join('%s/%s#%d-%d(%d)' % (k[0], k[1], min(v), max(v), len(v)) for k, v in ch.items())
    print('%d  n=%d  %s' % (n, len(recs), s))
