# -*- coding: utf-8 -*-
"""Heuristic check: for each 記段, rank 鈔段 by shared-char-bigram overlap."""
import io, os, re, sys, json
sys.stdout.reconfigure(encoding='utf-8')
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
D = os.path.join(B, 'AI語譯', '_work', 'align_fix')

def load(fn, tag):
    s = io.open(os.path.join(D, fn), encoding='utf-8').read()
    out = {}
    for m in re.finditer(r'\[' + tag + r'(\d+)\] (.*?)(?=\n\n|\Z)', s, re.S):
        out[int(m.group(1))] = m.group(2).strip()
    return out

Z = load('_a019_ji.txt', 'z')
C = load('_a019_cao.txt', 'c')
J = json.load(io.open(os.path.join(D, '019.json'), encoding='utf-8'))
zs = [it['z'] for it in J['items']]

def bg(s):
    s = re.sub(r'[^\u4e00-\u9fff]', '', s)
    return set(s[i:i+2] for i in range(len(s)-1))

cb = {c: bg(t) for c, t in C.items()}
for z in zs:
    head = Z[z][:45]
    full = Z[z]
    hb = bg(head); fb = bg(full)
    sc = []
    for c in C:
        s1 = len(hb & cb[c]) / max(1, len(hb))
        s2 = len(fb & cb[c]) / max(1, len(fb))
        sc.append((0.65*s1 + 0.35*s2, c))
    sc.sort(reverse=True)
    top = ' '.join('c%d:%.2f' % (c, s) for s, c in sc[:4])
    print('z%-4d %s | %s' % (z, top, head[:30]))
