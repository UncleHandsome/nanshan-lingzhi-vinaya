# -*- coding: utf-8 -*-
"""以 _m2 備份核對：段數、行尾、累計相異段。用法: python _zx1031_check.py 資持記/05b_上四 [..]"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import _r2a_lib as L

BKM2 = os.path.join(L.ROOT, '歸檔', 'r2修正前', '資持記')

for a in sys.argv[1:]:
    book, chunk = a.split('/')
    cur = L.Out(book, chunk)
    bp = os.path.join(BKM2, chunk + '_m2.txt')
    if not os.path.exists(bp):
        print('%s/%s: NO M2 BACKUP' % (book, chunk))
        continue
    bs = L.decode(L.rd(bp))
    beol = '\r\n' if '\r\n' in bs else '\n'
    bparts = bs.split(beol + beol)
    if bparts and bparts[-1] == '':
        bparts = bparts[:-1]
    diffs = [i + 1 for i in range(min(len(bparts), len(cur.segs))) if bparts[i] != cur.segs[i]]
    print('%s/%s: seg %d->%d eol %r->%r diffsegs=%d' % (book, chunk, len(bparts), len(cur.segs), beol, cur.eol, len(diffs)))
