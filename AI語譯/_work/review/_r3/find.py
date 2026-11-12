# -*- coding: utf-8 -*-
"""find.py NNN "phrase" ["phrase" ...] [--w=60] -- locate phrases in the out text of
校閱_NNN's chunks and print a context window around the best match.

For each phrase: best paragraph + best matching offset (longest common block).
Output:
  #i [<book>/<chunk>#<line>] r=<ratio> …left【MATCH】right…
"""
import os, re, sys, difflib
sys.stdout.reconfigure(encoding='utf-8')
ROOT = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
OUT = os.path.join(ROOT, 'AI語譯', 'out')
MAT = os.path.join(ROOT, '校閱_10K')
LBL = re.compile(r'^【(\d{3})-(\d{4})】(.+?)/(.+?)#(\d+)\s*$')
W = 65
args = []
for a in sys.argv[1:]:
    if a.startswith('--w='):
        W = int(a[4:])
    else:
        args.append(a)
nnn = args[0].zfill(3)
phrases = args[1:]
t = open(os.path.join(MAT, '校閱_%s.txt' % nnn), 'rb').read().decode('utf-8-sig')
chunks = []
for ln in t.split('\n'):
    m = LBL.match(ln.rstrip('\r'))
    if m:
        k = (m.group(3), m.group(4))
        if k not in chunks:
            chunks.append(k)
paras = []
for book, chunk in chunks:
    lines = open(os.path.join(OUT, book, chunk + '.txt'), 'rb').read().decode('utf-8-sig').split('\n')
    for i, s in enumerate(lines):
        s = s.rstrip('\r')
        if s.strip():
            paras.append((book, chunk, i + 1, s))
print('## %s  chunks=%s paras=%d' % (nnn, ','.join('%s/%s' % c for c in chunks), len(paras)))
for k, ph in enumerate(phrases, 1):
    ph = ph.strip()
    best = (-1.0, None, 0, 0)
    for book, chunk, ln, s in paras:
        sm = difflib.SequenceMatcher(None, s, ph)
        blocks = [b for b in sm.get_matching_blocks() if b.size]
        cov = sum(b.size for b in blocks) / max(1, len(ph))
        if cov > best[0]:
            big = max(blocks, key=lambda b: b.size) if blocks else None
            best = (cov, (book, chunk, ln, s), big.a if big else 0, big.size if big else 0)
    cov, loc, a, size = best
    if loc is None:
        print('#%d %s  NO HIT' % (k, ph[:40])); continue
    book, chunk, ln, s = loc
    lo, hi = max(0, a - W), min(len(s), a + size + W)
    print('#%d cov=%.2f [%s/%s#%d] %s' % (k, cov, book, chunk, ln, ph[:60]))
    print('   %s%s%s%s%s' % ('…' if lo else '', s[lo:a], '【', s[a:a + size], '】' + s[a + size:hi] + ('…' if hi < len(s) else '')))
