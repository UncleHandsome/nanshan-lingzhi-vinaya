# -*- coding: utf-8 -*-
"""Diagnostic: bigram overlap between each 記段 and each 鈔段, vs assigned c."""
import io, json, os, re, sys
sys.stdout.reconfigure(encoding='utf-8')

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
AD = os.path.join(B, 'AI語譯', '_work', 'align_fix')


def load(p):
    txt = io.open(p, encoding='utf-8').read()
    out = {}
    for part in txt.split('\n\n'):
        part = part.strip()
        if not part:
            continue
        m = re.match(r'\[(z|c)(\d+)\] len=(\d+)\n(.*)$', part, re.S)
        if m:
            out[int(m.group(2))] = m.group(4)
    return out


Z = load(os.path.join(AD, '_a015_Z.txt'))
C = load(os.path.join(AD, '_a015_C.txt'))
MAP = [m['c'] for m in json.load(io.open(os.path.join(AD, 'out_015.json'), encoding='utf-8'))['map']]


def bg(s):
    s = re.sub(r'[^\u4e00-\u9fff]', '', s)
    return set(s[i:i + 2] for i in range(len(s) - 1))


bad = []
for zi in range(150):
    z = bg(Z[zi])
    scores = sorted(((len(z & bg(C[ci])) / max(1, len(z)), ci) for ci in C), reverse=True)
    top = scores[:4]
    a = MAP[zi]
    if all(ci != a for _, ci in top):
        bad.append((zi, a, [(round(s, 2), ci) for s, ci in top]))
print('assigned c not in top4 bigram overlap:', len(bad))
for b in bad:
    print(b)
# also show rank of assigned c stats
ranks = []
for zi in range(150):
    z = bg(Z[zi])
    sc = sorted(((len(z & bg(C[ci])) / max(1, len(z)), ci) for ci in C), reverse=True)
    r = [ci for _, ci in sc].index(MAP[zi])
    ranks.append(r)
print('median rank', sorted(ranks)[len(ranks) // 2], 'mean rank', round(sum(ranks) / len(ranks), 1))
