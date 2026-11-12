# -*- coding: utf-8 -*-
"""以 _m3 備份核對段數、行尾。用法: python _zx2_check.py 資持記/05d_上四 [..]"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _r2a_lib as L

BKM3 = os.path.join(L.ROOT, '歸檔', 'r2修正前', '資持記')

for a in sys.argv[1:]:
    book, chunk = a.split('/')
    cur = L.Out(book, chunk)
    bp = os.path.join(BKM3, chunk + '_m3.txt')
    if not os.path.exists(bp):
        print('%s/%s: NO M3 BACKUP' % (book, chunk))
        continue
    bs = L.decode(L.rd(bp))
    beol = '\r\n' if '\r\n' in bs else '\n'
    bparts = bs.split(beol + beol)
    if bparts and bparts[-1] == '':
        bparts = bparts[:-1]
    diffs = [i + 1 for i in range(min(len(bparts), len(cur.segs))) if bparts[i] != cur.segs[i]]
    print('%s/%s: seg %d->%d eol %r->%r diffsegs=%d' % (book, chunk, len(bparts), len(cur.segs), beol, cur.eol, len(diffs)))
