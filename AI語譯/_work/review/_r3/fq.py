# -*- coding: utf-8 -*-
"""fq.py NNN "phrase" ... -- print FULL current out paragraphs containing each phrase,
searching every chunk referenced by 校閱_NNN.txt. Shows chunk, line no, occurrences."""
import os, re, sys
sys.stdout.reconfigure(encoding='utf-8')
ROOT = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
OUT = os.path.join(ROOT, 'AI語譯', 'out')
MAT = os.path.join(ROOT, '校閱_10K')
LBL = re.compile(r'^【(\d{3})-(\d{4})】(.+?)/(.+?)#(\d+)\s*$')

nnn = sys.argv[1].zfill(3)
phr = sys.argv[2:]
keys = []
for ln in open(os.path.join(MAT, '校閱_%s.txt' % nnn), 'rb').read().decode('utf-8-sig').split('\n'):
    m = LBL.match(ln.rstrip('\r'))
    if m:
        k = (m.group(3), m.group(4))
        if k not in keys:
            keys.append(k)
for p in phr:
    print('@@ %s' % p)
    n = 0
    for book, chunk in keys:
        t = open(os.path.join(OUT, book, chunk + '.txt'), 'rb').read().decode('utf-8-sig')
        for i, s in enumerate(t.split('\n')):
            s2 = s.rstrip('\r')
            if p in s2:
                print('  [%s #%d x%d] %s' % (chunk, i + 1, s2.count(p), s2))
                n += 1
    if not n:
        print('  (no hit)')
