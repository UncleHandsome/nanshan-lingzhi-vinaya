# -*- coding: utf-8 -*-
import importlib.util, sys, io
spec = importlib.util.spec_from_file_location("fx", r"C:\Users\lionc\OneDrive\桌面\XW\三大部\_src\fix_hebian_jz2.py")
fx = importlib.util.module_from_spec(spec); spec.loader.exec_module(fx)
yp = fx.yuan_pairs(); yp, A = fx.assign(yp)
# 每單元 記 是否連續
seq = [(i, r['num'], r['sub'], r['u']) for i, r in enumerate(yp) if r['kind']=='記']
bad = []
for u in range(1, len(fx.UNIT)+1):
    idxs = [j for j,(i,num,sub,uu) in enumerate(seq) if uu==u]
    if idxs and idxs != list(range(idxs[0], idxs[0]+len(idxs))):
        bad.append((u, fx.UNIT[u-1][0], [seq[j][1] for j in idxs]))
print('記段非連續的單元:', bad)
# 每單元 鈔 是否連續（應為連續，除了本來就分段）
cs = [(i, r['num'], r['u']) for i, r in enumerate(yp) if r['kind']=='鈔']
badc = []
for u in range(1, len(fx.UNIT)+1):
    idxs = [j for j,(i,num,uu) in enumerate(cs) if uu==u]
    if idxs != list(range(idxs[0], idxs[0]+len(idxs))):
        badc.append((u, fx.UNIT[u-1][0]))
print('鈔段非連續的單元:', badc)
print('單元數', len(set(r['u'] for r in yp if r['kind']=='鈔')), '記單元', len(set(r['u'] for r in yp if r['kind']=='記')))
# LIS 計算實際搬移段數
def lis_count(order):
    import bisect
    tails = []
    for x in order:
        i = bisect.bisect_left(tails, x)
        if i == len(tails): tails.append(x)
        else: tails[i] = x
    return len(tails)
import importlib
cl = yp  # 原始順序即 cl
for mode in ('block','pair'):
    order = fx.block_order(cl) if mode=='block' else fx.pair_order(cl)
    n = lis_count(order)
    print(mode, '位置變動', sum(1 for k in range(376) if order[k]!=k), '相對順序實際搬移', 376-n)
