# -*- coding: utf-8 -*-
"""Balance-check changed paragraphs: brackets/quotes parity, no stray edit artifacts."""
import os, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
ROOT = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
BAK = os.path.join(ROOT, '歸檔', 'r3修正前')
OUT = os.path.join(ROOT, 'AI語譯', 'out')
PAIRS = {'（': '）', '「': '」', '〔': '〕', '《': '》', '『': '』'}

def paras(p):
    t = open(p, 'rb').read().decode('utf-8-sig')
    return [s.rstrip('\r') for s in t.split('\n') if s.rstrip('\r').strip()]

bad = 0
for book in os.listdir(BAK):
    bd = os.path.join(BAK, book)
    if not os.path.isdir(bd):
        continue
    for f in sorted(os.listdir(bd)):
        if not os.path.exists(os.path.join(OUT, book, f)):
            continue
        a = paras(os.path.join(bd, f))
        b = paras(os.path.join(OUT, book, f))
        for i, (x, y) in enumerate(zip(a, b)):
            if x == y:
                continue
            for o, c in PAIRS.items():
                if y.count(o) != y.count(c):
                    print('UNBAL %s/%s #%d  %s%d/%s%d' % (book, f, i + 1, o, y.count(o), c, y.count(c)))
                    print('   ', y[:120])
                    bad += 1
print('unbalanced', bad)
