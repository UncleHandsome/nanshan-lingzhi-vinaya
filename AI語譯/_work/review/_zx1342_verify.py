# -*- coding: utf-8 -*-
"""驗證：備份(_j) vs 現行，段數、行尾、相異段數。"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import _zx1342_lib as L

out = []
for book, chunk in [('資持記', '15d_下三'), ('資持記', '15e_下三')]:
    cur = L.Out(book, chunk)
    bk = os.path.join(L.BKBASE, book, chunk + '_j.txt')
    if not os.path.exists(bk):
        out.append('%s/%s NO BACKUP' % (book, chunk))
        continue
    b = open(bk, 'rb').read().decode('utf-8')
    beol = '\r\n' if '\r\n' in b else '\n'
    bparts = b.split(beol + beol)
    if bparts and bparts[-1] == '':
        bparts = bparts[:-1]
    diff = [i + 1 for i in range(min(len(bparts), len(cur.segs)))
            if bparts[i] != cur.segs[i]]
    out.append('%s/%s bak_segs=%d cur_segs=%d eol=%s/%s diff=%d %s' % (
        book, chunk, len(bparts), len(cur.segs), repr(beol), repr(cur.eol),
        len(diff), diff))
open(os.path.join(os.path.dirname(__file__), '_zx1342_verify.txt'), 'w',
     encoding='utf-8').write('\n'.join(out))
print('\n'.join(out))
