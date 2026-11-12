# -*- coding: utf-8 -*-
"""pshow.py book/chunk kw1 [kw2 ...] -- print full paragraphs of out file containing kw."""
import os, sys
sys.stdout.reconfigure(encoding='utf-8')
ROOT = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
OUT = os.path.join(ROOT, 'AI語譯', 'out')
book, chunk = sys.argv[1].split('/')
p = os.path.join(OUT, book, chunk + '.txt')
raw = open(p, 'rb').read()
t = raw.decode('utf-8-sig')
lines = t.split('\n')
for kw in sys.argv[2:]:
    print('@@ %s' % kw)
    n = 0
    for i, s in enumerate(lines):
        s2 = s.rstrip('\r')
        if kw in s2:
            print('#%d %s' % (i + 1, s2))
            n += 1
    if not n:
        print('  (no hit)')
