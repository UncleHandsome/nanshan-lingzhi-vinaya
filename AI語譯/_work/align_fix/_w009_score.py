# -*- coding: utf-8 -*-
"""逐 z 計算與各鈔段的最長共同子串（漢字），列出候選。"""
import io, os, re, json, sys
sys.stdout.reconfigure(encoding='utf-8')
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\align_fix'
d = json.load(io.open(os.path.join(D, '_w009_data.json'), encoding='utf-8'))
J, C = d['ji'], d['cao']
han = lambda s: ''.join(re.findall(r'[\u4e00-\u9fff]', s))
JH = [han(x) for x in J]
CH = [han(x) for x in C]
MIN = 6
IDX = {}
for c, t in enumerate(CH):
    seen = set()
    for i in range(len(t) - MIN + 1):
        s = t[i:i+MIN]
        if s in seen:
            continue
        seen.add(s)
        IDX.setdefault(s, set()).add(c)


def score(z):
    jz = JH[z]
    best = {}
    n = len(jz)
    for L in range(min(n, 30), MIN - 1, -1):
        for i in range(0, n - L + 1):
            s = jz[i:i+L]
            if s in IDX:
                for c in IDX[s]:
                    if best.get(c, 0) < L:
                        best[c] = L
    return best


lo = int(sys.argv[1]) if len(sys.argv) > 1 else 440
hi = int(sys.argv[2]) if len(sys.argv) > 2 else 610
for z in range(lo, hi):
    b = score(z)
    top = sorted(b.items(), key=lambda kv: -kv[1])[:5]
    print('z%-4d %s' % (z, '  '.join('c%d:%d' % (c, L) for c, L in top)))
