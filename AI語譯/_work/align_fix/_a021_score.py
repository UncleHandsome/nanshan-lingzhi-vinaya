# -*- coding: utf-8 -*-
"""Rank 鈔段 for each 記段 by char-bigram overlap (for sec19 batch 021)."""
import io, os, re, json, sys
sys.stdout.reconfigure(encoding='utf-8')
D = os.path.join(r'C:\Users\lionc\OneDrive\桌面\XW\三大部', 'AI語譯', '_work', 'align_fix')

def load(fn, tag):
    s = io.open(os.path.join(D, fn), encoding='utf-8').read()
    out = {}
    for m in re.finditer(r'\[' + tag + r'(\d+)\] (.*?)(?=\n\n|\Z)', s, re.S):
        out[int(m.group(1))] = m.group(2).strip()
    return out

Z = load('_a021_ji.txt', 'z')
C = load('_a021_cao.txt', 'c')

def bg(s):
    s = re.sub(r'[^\u4e00-\u9fff]', '', s)
    return set(s[i:i+2] for i in range(len(s)-1))

cb = {c: bg(t) for c, t in C.items()}
for z in sorted(Z):
    t = Z[z]
    head = t[:50]
    tb = bg(t)
    sc = []
    for c in C:
        inter = len(tb & cb[c])
        sc.append((inter / max(1, len(tb)), inter, c))
    sc.sort(reverse=True)
    print('z%-2d %s' % (z, '  '.join('c%d:%.2f/%d' % (c, s, n) for s, n, c in sc[:5])))
