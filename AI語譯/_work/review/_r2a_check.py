# -*- coding: utf-8 -*-
"""驗證：目前 out 與 _g 備份比對（段數、行尾、相異段）。用法: python _r2a_check.py 書 chunk [chunk2...]"""
import os, sys, difflib
sys.path.insert(0, os.path.dirname(__file__))
import _r2a_lib as L

books = {}
for a in sys.argv[1:]:
    book, chunk = a.split('/')
    books.setdefault(book, []).append(chunk)

for book, chunks in books.items():
    for chunk in chunks:
        cur = L.Out(book, chunk)
        bp = os.path.join(L.BKBASE, book, chunk + '_g.txt')
        if not os.path.exists(bp):
            print('%s/%s: NO BACKUP' % (book, chunk))
            continue
        bs = L.decode(L.rd(bp))
        beol = '\r\n' if '\r\n' in bs else '\n'
        bparts = bs.split(beol + beol)
        if bparts and bparts[-1] == '':
            bparts = bparts[:-1]
        diffs = [i + 1 for i in range(min(len(bparts), len(cur.segs)))
                 if bparts[i] != cur.segs[i]]
        print('%s/%s: seg %d->%d eol %s->%s diffsegs=%d %s' % (
            book, chunk, len(bparts), len(cur.segs), repr(beol), repr(cur.eol),
            len(diffs), diffs))
