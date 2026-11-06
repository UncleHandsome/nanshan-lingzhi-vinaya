# -*- coding: utf-8 -*-
import io, os, re, sys
sys.stdout.reconfigure(encoding='utf-8')
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\align_fix'
def load(fn, tag):
    s = io.open(os.path.join(D, fn), encoding='utf-8').read()
    out = {}
    for m in re.finditer(r'\[' + tag + r'(\d+)\] (.*?)(?=\n\n|\Z)', s, re.S):
        out[int(m.group(1))] = m.group(2).strip()
    return out
Z = load('_t020_ji.txt', 'z'); C = load('_t020_cao.txt', 'c')
def bg(s):
    s = re.sub(r'[^\u4e00-\u9fff]', '', s)
    return set(s[i:i+2] for i in range(len(s)-1))
cb = {c: bg(t) for c, t in C.items()}
for z in sorted(Z):
    hb = bg(Z[z][:40])
    sc = []
    for c in cb:
        s1 = len(hb & cb[c]) / max(1, len(hb))
        s2 = len(bg(Z[z]) & cb[c]) / max(1, len(bg(Z[z])))
        sc.append((0.6*s1 + 0.4*s2, c))
    sc.sort(reverse=True)
    print('z%-4d %s || %s' % (z, ' '.join('c%d:%.2f' % (c, s) for s, c in sc[:4]), Z[z][:24]))
