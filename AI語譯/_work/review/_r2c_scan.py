# -*- coding: utf-8 -*-
"""掃描 1342-1490：每檔段數、來源書/chunk、相似度是否 >=0.94、resp 是否存在。"""
import os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
import _r2c_lib as L

rows = []
for n in range(1342, 1491):
    rp = os.path.join(L.RESP, 'resp_%04d.txt' % n)
    has_resp = os.path.exists(rp)
    rsz = os.path.getsize(rp) if has_resp else 0
    try:
        recs = L.parse_review(n)
    except Exception as e:
        rows.append(dict(n=n, err=str(e), resp=has_resp, rsz=rsz))
        continue
    info = []
    bad = 0
    for r in recs:
        seg, ratio, moved = L.locate(r['book'], r['chunk'], r['trans'], r['seg'])
        if moved or ratio < 0.94:
            bad += 1
        info.append((r['seq'], r['book'], r['chunk'], r['seg'], seg, round(ratio, 3), moved))
    rows.append(dict(n=n, resp=has_resp, rsz=rsz, nseg=len(recs), bad=bad,
                     books=sorted(set(x[1] for x in info)),
                     chunks=sorted(set('%s/%s' % (x[1], x[2]) for x in info)),
                     info=info))
json.dump(rows, open(os.path.join(os.path.dirname(__file__), '_r2c_scan.json'), 'w',
                     encoding='utf-8'), ensure_ascii=False, indent=0)
tot = sum(r.get('nseg', 0) for r in rows)
print('files=%d segs=%d' % (len(rows), tot))
for r in rows:
    if 'err' in r:
        print('%d ERR %s' % (r['n'], r['err']))
        continue
    flag = '' if r['bad'] == 0 else ' BAD=%d' % r['bad']
    nr = '' if r['resp'] else ' NO_RESP'
    print('%d segs=%d resp=%d%s%s %s' % (r['n'], r['nseg'], r['rsz'], nr, flag,
                                         ','.join(r['chunks'])[:80]))
