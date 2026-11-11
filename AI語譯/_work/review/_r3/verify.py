# -*- coding: utf-8 -*-
"""Verify r3 edits: paragraph counts unchanged, no new duplicates, diff summary."""
import os, sys, re, collections
sys.stdout.reconfigure(encoding='utf-8')
ROOT = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
BAK = os.path.join(ROOT, '歸檔', 'r3修正前')
OUT = os.path.join(ROOT, 'AI語譯', 'out')

def paras(p):
    t = open(p, 'rb').read().decode('utf-8-sig')
    return [s.rstrip('\r') for s in t.split('\n') if s.rstrip('\r').strip()]

tot = 0
for book in os.listdir(BAK):
    bd = os.path.join(BAK, book)
    if not os.path.isdir(bd):
        continue
    for f in sorted(os.listdir(bd)):
        if not os.path.exists(os.path.join(OUT, book, f)):
            continue
        a = paras(os.path.join(bd, f))
        b = paras(os.path.join(OUT, book, f))
        tot += 1
        status = 'OK' if len(a) == len(b) else 'COUNT-MISMATCH %d->%d' % (len(a), len(b))
        dupA = [k for k, v in collections.Counter(a).items() if v > 1]
        dupB = [k for k, v in collections.Counter(b).items() if v > 1]
        nd = len(set(map(tuple, dupB)) - set(map(tuple, dupA)))
        print('%-10s %-14s paras=%d %s dup_new=%d' % (book, f, len(b), status, nd))
        if status != 'OK':
            for i, (x, y) in enumerate(zip(a, b)):
                if x != y:
                    print('   first diff at #%d' % (i + 1)); break
print('files', tot)
