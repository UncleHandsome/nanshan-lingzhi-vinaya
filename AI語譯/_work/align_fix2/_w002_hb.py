# -*- coding: utf-8 -*-
import csv, io, os, sys

p = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\合編材料\篇27_諸雜要行.csv'
with io.open(p, encoding='utf-8-sig', newline='') as f:
    rows = list(csv.reader(f))
print('rows', len(rows))
hdr = rows[0]
print('hdr', hdr)
out = []
cao_idx = 0
for i, r in enumerate(rows[1:], start=1):
    if not r or not r[0].strip():
        continue
    t = r[0].strip()
    seq = r[1].strip() if len(r) > 1 else ''
    txt = r[2].strip() if len(r) > 2 else ''
    mapv = r[4].strip() if len(r) > 4 else ''
    out.append('%s|%s|map=%s|%s' % (t, seq, mapv, txt[:50]))
io.open(os.path.join(os.path.dirname(__file__), '_w002_hb.txt'), 'w', encoding='utf-8').write('\n'.join(out))
print('written', len(out))
