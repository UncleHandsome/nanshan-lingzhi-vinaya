# -*- coding: utf-8 -*-
"""普查 1371-1490：段數、書/chunk、回應檔大小、定位 ratio。"""
import os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
import _zx1353_lib as L

rows = []
for n in range(1371, 1491):
    recs = L.parse_review(n)
    books = sorted(set((r['book'], r['chunk']) for r in recs))
    rp = os.path.join(L.RESP, 'resp_%d.txt' % n)
    size = os.path.getsize(rp) if os.path.exists(rp) else -1
    bad = []
    for r in recs:
        seg, ratio, moved = L.locate(r['book'], r['chunk'], r['trans'], r['seg'])
        if ratio < 0.94 or moved:
            bad.append('%d:%d->%d:%.3f' % (r['seq'], r['seg'], seg, ratio))
    rows.append(dict(n=n, nseg=len(recs), books=['%s/%s' % b for b in books],
                     size=size, bad=bad,
                     seqs=[r['seq'] for r in recs]))
    print('%d segs=%d %s resp=%s bad=%s' % (n, len(recs), ','.join('%s/%s' % b for b in books), size, ';'.join(bad)))
json.dump(rows, open(os.path.join(os.path.dirname(__file__), '_zx1371_survey.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
