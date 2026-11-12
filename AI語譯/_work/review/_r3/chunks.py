# -*- coding: utf-8 -*-
"""chunks.py NNN [...] -- print chunk list for each resp NNN from 校閱_10K labels."""
import os, re, sys
sys.stdout.reconfigure(encoding='utf-8')
ROOT = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
MAT = os.path.join(ROOT, '校閱_10K')
LBL = re.compile(r'^【(\d{3})-(\d{4})】(.+?)/(.+?)#(\d+)\s*$')

for a in sys.argv[1:]:
    n = a.zfill(3)
    p = os.path.join(MAT, '校閱_%s.txt' % n)
    if not os.path.exists(p):
        print(n, 'MISSING')
        continue
    seen = []
    nblk = 0
    for ln in open(p, 'rb').read().decode('utf-8-sig').split('\n'):
        m = LBL.match(ln.rstrip('\r'))
        if m:
            nblk += 1
            k = (m.group(3), m.group(4))
            if k not in seen:
                seen.append(k)
    print(n, 'blk=%d' % nblk, ' | '.join(x + '/' + y for x, y in seen))
