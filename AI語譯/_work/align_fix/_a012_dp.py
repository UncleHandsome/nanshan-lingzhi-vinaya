# -*- coding: utf-8 -*-
"""DP monotone alignment (cross-check) of z900-1049 to c0-319 by shared n-grams."""
import io, os, re, json, importlib.util, sys
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8')

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
AD = os.path.join(B, 'AI語譯', '_work', 'align_fix')
spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)
SECS, ZS = ex.sections(), ex.zsecs()
SKIP1 = re.compile(r'^\d+\s*[\u4e00-\u9fff]{2,10}篇\(上[一二三四五六七八九十]?\)$')
SKIP2 = re.compile(r'^[\u4e00-\u9fff]{2,10}篇第[一二三四五六七八九十]+$')
IDX = 13
C = [o for o, t in SECS[IDX]['items'] if not SKIP1.match(o.strip()) and not SKIP2.match(o.strip())]
Z = [o for o, t in ex.zitems_for(IDX, ZS)]

def grams(s, n):
    h = re.sub(r'[^\u4e00-\u9fff]', '', s)
    return Counter(h[i:i+n] for i in range(0, max(0, len(h)-n+1)))

C3 = [grams(c,3) for c in C]; C2 = [grams(c,2) for c in C]
Z3 = [grams(z,3) for z in Z]; Z2 = [grams(z,2) for z in Z]

def sim(z, c):
    a = sum((Z3[z] & C3[c]).values())
    b = sum((Z2[z] & C2[c]).values())
    return 3.0*a + 0.6*b

zs = list(range(900, 1050))
# DP: allow start >= 140, non-decreasing c, skip allowed
cand = list(range(140, 216))
S = [[sim(z, c) for c in cand] for z in zs]
nz, nc = len(zs), len(cand)
NEG = -1e18
best = [[NEG]*nc for _ in range(nz)]
prev = [[-1]*nc for _ in range(nz)]
for j in range(nc):
    best[0][j] = S[0][j]
for i in range(1, nz):
    runmax, runidx = NEG, -1
    for j in range(nc):
        # best previous with index <= j
        if best[i-1][j] > runmax:
            runmax, runidx = best[i-1][j], j
        best[i][j] = runmax + S[i][j]
        prev[i][j] = runidx
j = max(range(nc), key=lambda k: best[nz-1][k])
path = [0]*nz
for i in range(nz-1, -1, -1):
    path[i] = j
    j = prev[i][j]
res = {zs[i]: cand[path[i]] for i in range(nz)}
out = io.StringIO()
for z in zs:
    out.write('z%d -> c%d\n' % (z, res[z]))
io.open(os.path.join(AD, '_a012_dp.txt'), 'w', encoding='utf-8').write(out.getvalue())
print('DP done, total', sum(S[i][path[i]] for i in range(nz)))
# show compact run-length
runs=[]
for z in zs:
    c=res[z]
    if runs and runs[-1][0]==c: runs[-1][1]+=1
    else: runs.append([c,1])
print('runs:', ' '.join('c%d x%d' % (c,n) for c,n in runs))
