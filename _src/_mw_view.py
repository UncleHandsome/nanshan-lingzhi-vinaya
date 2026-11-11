# -*- coding: utf-8 -*-
"""檢視 _mw_rows.txt：依詞列印，含上下文。"""
import io, sys, collections

P = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\_src\_mw_rows.txt'
rows = []
for ln in io.open(P, encoding='utf-8'):
    f = ln.rstrip('\n').split('\t')
    if len(f) >= 8:
        rows.append(f)

want = sys.argv[1:] if len(sys.argv) > 1 else None
if want:
    sel = [r for r in rows if r[3] in want]
else:
    sel = rows

by = collections.OrderedDict()
for r in sel:
    by.setdefault(r[3], []).append(r)

for w, rs in by.items():
    print('===== %s (%d) =====' % (w, len(rs)))
    for bk, fn, para, _, n, l, rr, sent in rs:
        tag = '01' if bk.startswith('01') else '02'
        print('%s %s:%s x%s' % (tag, fn, para, n))
        print('   …%s【%s】%s…' % (l, w, rr))
    print()
