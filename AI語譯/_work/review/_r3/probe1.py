# -*- coding: utf-8 -*-
import os, re, sys, difflib
sys.stdout.reconfigure(encoding='utf-8')
ROOT = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
OUT = os.path.join(ROOT, 'AI語譯', 'out')
MAT = os.path.join(ROOT, '校閱_10K')

def paras(book, chunk):
    t = open(os.path.join(OUT, book, chunk + '.txt'), 'rb').read().decode('utf-8-sig')
    return [s for s in (x.rstrip('\r') for x in t.split('\n')) if s.strip()]

def labels(nnn):
    t = open(os.path.join(MAT, '校閱_%s.txt' % nnn), 'rb').read().decode('utf-8-sig')
    return re.findall(r'^【(\d{3})-(\d{4})】(.+?)/(.+?)#(\d+)\s*$', t, re.M)

print('--- 021 labels tail / 022 labels ---')
for n in ('021', '022', '023', '025', '026'):
    L = labels(n)
    print(n, 'n=', len(L), 'first3', [(a, b, c, d, e) for a, b, c, d, e in L[:3]],
          'segs', [int(x[4]) for x in L][:8], '...', [int(x[4]) for x in L][-3:])
