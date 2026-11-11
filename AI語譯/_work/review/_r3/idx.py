# -*- coding: utf-8 -*-
import os, re, sys
sys.stdout.reconfigure(encoding='utf-8')
ROOT = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
MAT = os.path.join(ROOT, '校閱_10K')
LBL = re.compile(r'^【(\d{3})-(\d{4})】(.+?)/(.+?)#(\d+)\s*$')
for n in range(39, 181):
    p = os.path.join(MAT, '校閱_%03d.txt' % n)
    if not os.path.exists(p):
        print(n, 'MISSING')
        continue
    t = open(p, 'rb').read().decode('utf-8-sig')
    keys = []
    cnt = 0
    for ln in t.split('\n'):
        m = LBL.match(ln.rstrip('\r'))
        if m:
            cnt += 1
            k = (m.group(3), m.group(4))
            if k not in keys:
                keys.append(k)
    print('%03d\t%d\t%s' % (n, cnt, ' | '.join('%s/%s' % k for k in keys)))
