# -*- coding: utf-8 -*-
import json, io, os, re, difflib

base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
W = os.path.join(base, 'AI語譯', '_work')

def load_full(p):
    out = {}
    for line in io.open(p, encoding='utf-8'):
        line = line.strip()
        if not line:
            continue
        m = re.match(r'^\[([zc])(\d+)\]\s*(.*)$', line)
        if m:
            out[int(m.group(2))] = m.group(3)
    return out

fullz = load_full(os.path.join(W, 'align_fix', '_tmp029_ji_full.txt'))
fullc = load_full(os.path.join(W, 'align_fix', '_tmp029_cao_full.txt'))

cao = ''
cstart = {}
for c in sorted(fullc):
    cstart[c] = len(cao)
    cao += fullc[c]
cids = sorted(fullc)
cposes = [cstart[c] for c in cids]

import bisect
def c_of(pos):
    i = bisect.bisect_right(cposes, pos) - 1
    return cids[i]

# weight matrix: score[z][c]
items = json.load(io.open(os.path.join(W, 'align_fix2', '002.json'), encoding='utf-8'))['items']
zs = [it['z'] for it in items]
score = {}
detail = {}
for z in zs:
    seg = fullz[z]
    sm = difflib.SequenceMatcher(None, seg, cao, autojunk=False)
    blocks = [b for b in sm.get_matching_blocks() if b.size >= 3]
    sc = {}
    det = {}
    for b in blocks:
        c = c_of(b.b)
        w = b.size * b.size
        sc[c] = sc.get(c, 0) + w
        det.setdefault(c, []).append((b.size, seg[b.a:b.a + b.size]))
    score[z] = sc
    detail[z] = det

# DP for best monotonic path
zc = len(zs)
co = len(cids)
NEG = -10**9
dp = [[NEG] * co for _ in range(zc)]
bk = [[None] * co for _ in range(zc)]
for j, c in enumerate(cids):
    dp[0][j] = score[zs[0]].get(c, 0)
for i in range(1, zc):
    best = NEG; bi = None
    for j, c in enumerate(cids):
        if dp[i-1][j] > best:
            best = dp[i-1][j]; bi = j
        val = best + score[zs[i]].get(c, 0)
        dp[i][j] = val
        bk[i][j] = bi
# backtrack
end = max(range(co), key=lambda j: dp[zc-1][j])
path = [None] * zc
j = end
for i in range(zc-1, -1, -1):
    path[i] = cids[j]
    if i > 0:
        j = bk[i][j]

lines = []
lines.append('cao lens: ' + ', '.join('c%d=%d' % (c, len(fullc[c])) for c in cids))
lines.append('')
for i, z in enumerate(zs):
    sc = score[z]
    top = sorted(sc.items(), key=lambda kv: -kv[1])[:5]
    lines.append('z%-2d DP=%d  scores=%s' % (z, path[i], ' '.join('c%d:%d' % (c, s) for c, s in top)))
    for c, _ in top[:3]:
        lines.append('      c%-2d %s' % (c, ' '.join(repr(s) for _, s in detail[z][c][:6])))
lines.append('')
lines.append('DP path: ' + ','.join(str(x) for x in path))

io.open(os.path.join(os.path.dirname(__file__), '_a002_scores.txt'), 'w', encoding='utf-8').write('\n'.join(lines))
print('\n'.join(lines[:5]))
print('DP path:', path)
