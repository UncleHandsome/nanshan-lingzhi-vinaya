# -*- coding: utf-8 -*-
import io, os, re, sys, math
sys.stdout.reconfigure(encoding='utf-8')
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\align_fix'
def load(fn, tag):
    s = io.open(os.path.join(D, fn), encoding='utf-8').read()
    out = {}
    for m in re.finditer(r'\[' + tag + r'(\d+)\] (.*?)(?=\n\n|\Z)', s, re.S):
        out[int(m.group(1))] = m.group(2).strip()
    return out
Z = load('_t020_ji.txt', 'z'); C = load('_t020_cao.txt', 'c')
NZ = len(Z); NC = len(C)
def toks(s):
    s = re.sub(r'[^\u4e00-\u9fff]', '', s)
    return [s[i:i+2] for i in range(len(s)-1)]
docs = {('z',z): toks(t) for z,t in Z.items()}
docs.update({('c',c): toks(t) for c,t in C.items()})
df = {}
for k, ts in docs.items():
    for b in set(ts): df[b] = df.get(b,0)+1
N = len(docs)
idf = {b: math.log((N+1)/(d+1))+1 for b,d in df.items()}
def vec(ts):
    v = {}
    for b in ts: v[b] = v.get(b,0)+idf.get(b,1)
    n = math.sqrt(sum(x*x for x in v.values())) or 1
    return {b:x/n for b,x in v.items()}
VZ = {z: vec(t) for z,t in docs.items() if z[0]=='z'}
VC = {c: vec(t) for c,t in docs.items() if c[0]=='c'}
sim = {}
for z in range(NZ):
    for c in range(NC):
        a = VZ[('z',z)]; b = VC[('c',c)]
        sim[(z,c)] = sum(v*b.get(k,0) for k,v in a.items())
# position prior
zl = [len(re.sub(r'[^\u4e00-\u9fff]','',Z[z])) for z in range(NZ)]
cl = [len(re.sub(r'[^\u4e00-\u9fff]','',C[c])) for c in range(NC)]
Zcum = [0]
for x in zl: Zcum.append(Zcum[-1]+x)
Ccum = [0]
for x in cl: Ccum.append(Ccum[-1]+x)
ZT = Zcum[-1]; CT = Ccum[-1]
def pos_cost(z,c,lam=1.2):
    # 記 position fraction vs 鈔 position fraction (center)
    pz = (Zcum[z]+zl[z]/2)/ZT
    pc = (Ccum[c]+cl[c]/2)/CT
    return lam*((pz-pc)**2)
BIG = -1e9
# DP over z, c nondecreasing ; maximize sim - pos_cost + switch penalty? allow jumps
dp = [[0.0]*NC for _ in range(NZ)]
bk = [[None]*NC for _ in range(NZ)]
for c in range(NC):
    dp[0][c] = sim[(0,c)] - pos_cost(0,c)
for z in range(1,NZ):
    best = BIG; bidx = 0
    for c in range(NC):
        # best previous c' <= c
        if dp[z-1][c] > best:
            best = dp[z-1][c]; bidx = c
        s = sim[(z,c)] - pos_cost(z,c)
        dp[z][c] = best + s
        bk[z][c] = bidx
# traceback
c = max(range(NC), key=lambda cc: dp[NZ-1][cc])
assign = [0]*NZ
for z in range(NZ-1,-1,-1):
    assign[z] = c
    if z>0: c = bk[z][c]
# print
from collections import Counter
cnt = Counter(assign)
print('groups:')
prev = None
for z in range(NZ):
    if assign[z]!=prev:
        print('c%-3d from z%-3d' % (assign[z], z))
        prev = assign[z]
print('used c:', ' '.join('c%d:%d'%(k,cnt[k]) for k in sorted(cnt)))
print('skipped:', [c for c in range(NC) if c not in cnt])
