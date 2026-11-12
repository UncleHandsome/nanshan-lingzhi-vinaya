# -*- coding: utf-8 -*-
"""以 _m4 備份核對段數、行尾。用法: python _zx3_check.py 資持記/06b_中一上 [...]"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _r2a_lib as L

BKM4 = os.path.join(L.ROOT, '歸檔', 'r2修正前', '資持記')

for a in sys.argv[1:]:
    book, chunk = a.split('/')
    cur = L.Out(book, chunk)
    bp = os.path.join(BKM4, chunk + '_m4.txt')
    if not os.path.exists(bp):
        print('%s/%s: NO M4 BACKUP' % (book, chunk))
        continue
    bs = L.decode(L.rd(bp))
    beol = '\r\n' if '\r\n' in bs else '\n'
    bparts = bs.split(beol + beol)
    if bparts and bparts[-1] == '':
        bparts = bparts[:-1]
    diffs = [i + 1 for i in range(min(len(bparts), len(cur.segs))) if bparts[i] != cur.segs[i]]
    print('%s/%s: seg %d->%d eol %r->%r diffsegs=%d' % (book, chunk, len(bparts), len(cur.segs), beol, cur.eol, len(diffs)))
