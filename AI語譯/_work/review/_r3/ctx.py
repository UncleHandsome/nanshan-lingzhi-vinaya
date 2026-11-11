# -*- coding: utf-8 -*-
"""ctx.py [--w N] kw1 [kw2 ...]  -- show context of keyword hits in AI語譯/out.

Prints one line per hit: file#para  ...context...
"""
import os, sys
sys.stdout.reconfigure(encoding='utf-8')
ROOT = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
OUT = os.path.join(ROOT, 'AI語譯', 'out')
args = sys.argv[1:]
w = 55
if args and args[0] == '--w':
    w = int(args[1]); args = args[2:]
# optional --book filter
book_only = None
if args and args[0].startswith('--b='):
    book_only = args[0][4:]; args = args[1:]

files = []
for book in sorted(os.listdir(OUT)):
    bd = os.path.join(OUT, book)
    if not os.path.isdir(bd):
        continue
    if book_only and book_only not in book:
        continue
    for f in sorted(os.listdir(bd)):
        if f.endswith('.txt'):
            files.append((book, f[:-4], os.path.join(bd, f)))

cache = []
for book, chunk, p in files:
    t = open(p, 'rb').read().decode('utf-8-sig')
    for i, ln in enumerate(t.split('\n')):
        s = ln.rstrip('\r')
        if s.strip():
            cache.append((book, chunk, i + 1, s))

for kw in args:
    print('### %s' % kw)
    n = 0
    for book, chunk, i, s in cache:
        st = 0
        while True:
            k = s.find(kw, st)
            if k < 0:
                break
            a, b = max(0, k - w), min(len(s), k + len(kw) + w)
            print('%s/%s#%d  %s%s%s' % (book, chunk, i, '…' if a else '', s[a:b], '…' if b < len(s) else ''))
            n += 1
            st = k + len(kw)
            if n > 40:
                break
        if n > 40:
            break
    if n == 0:
        print('  (no hit)')
