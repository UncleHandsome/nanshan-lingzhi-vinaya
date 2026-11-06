# -*- coding: utf-8 -*-
import csv, io, os, sys

base = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\合編材料'
files = sys.argv[1:] or ['篇26_瞻病送終.csv']
out = []
for fn in files:
    p = os.path.join(base, fn)
    with io.open(p, encoding='utf-8-sig', newline='') as f:
        rows = list(csv.reader(f))
    out.append('==== %s rows=%d ====' % (fn, len(rows)))
    nc = nz = 0
    for r in rows[1:]:
        if not r or not r[0].strip():
            continue
        t = r[0].strip(); seq = r[1].strip(); txt = r[2].strip() if len(r) > 2 else ''
        mapv = r[4].strip() if len(r) > 4 else ''
        if t == '鈔':
            nc += 1
            out.append('鈔%-3s %s' % (seq, txt[:46]))
        else:
            nz += 1
            out.append('    記%-3s -> %-3s | %s' % (seq, mapv, txt[:42]))
    out.append('counts 鈔=%d 記=%d' % (nc, nz))
io.open(os.path.join(os.path.dirname(__file__), '_w002_csv_chk.txt'), 'w', encoding='utf-8').write('\n'.join(out))
print('ok')
