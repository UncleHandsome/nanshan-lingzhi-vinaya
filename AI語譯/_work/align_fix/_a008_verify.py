# -*- coding: utf-8 -*-
"""最終驗證 out_008.json"""
import io, os, sys, json
sys.stdout.reconfigure(encoding='utf-8')
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\align_fix'
src = json.load(io.open(os.path.join(D, '008.json'), encoding='utf-8'))
out = json.load(io.open(os.path.join(D, 'out_008.json'), encoding='utf-8'))
M = out['map']
zs = [x['z'] for x in src['items']]
cs_valid = {x['c'] for x in src['cand']}
print('keys of out:', list(out.keys()))
print('map len:', len(M), 'items len:', len(zs))
assert len(M) == len(zs)
assert [x['z'] for x in M] == zs, 'z order/coverage mismatch'
c = [x['c'] for x in M]
assert all(isinstance(v, int) for v in c)
assert all(v in cs_valid for v in c), 'c not in cand'
assert all(c[i] <= c[i + 1] for i in range(len(c) - 1)), 'not non-decreasing'
print('z:', zs[0], '..', zs[-1], ' c:', min(c), '..', max(c))
print('monotone ok, all c in cand, entry keys:', sorted(M[0].keys()))
# 與前批(out_007)接續
o7 = json.load(io.open(os.path.join(D, 'out_007.json'), encoding='utf-8'))['map']
last7 = o7[-1]
print('out_007 last:', last7, ' out_008 first:', M[0], 'cross-batch monotone:', last7['c'] <= M[0]['c'])
# 檢查每個 c 都有記段，列出未使用的 c
used = sorted(set(c))
print('used c count', len(used), 'range used', used)
print('OK')
