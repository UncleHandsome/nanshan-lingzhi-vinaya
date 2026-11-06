# -*- coding: utf-8 -*-
"""業疏：以段落長度做單調對齊（DP），輸出每段對應的譯文全域索引"""
import io, os, re, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
S = os.path.join(B, 'TXT_分卷', '03_業疏')
T = os.path.join(B, 'AI語譯', 'out', '03_業疏')
OUT = os.path.join(B, 'AI語譯', '_work', 'ys_align_map.json')
han = lambda s: len(re.findall(r'[\u4e00-\u9fff]', s))

GAP = 0.45


def align(Ls, Lt):
    n, m = len(Ls), len(Lt)
    ms = sum(Ls) / max(1, n)
    mt = sum(Lt) / max(1, m)
    INF = 1e9
    dp = [[INF] * (m + 1) for _ in range(n + 1)]
    bk = [[None] * (m + 1) for _ in range(n + 1)]
    dp[0][0] = 0.0
    for i in range(n + 1):
        for j in range(m + 1):
            if i == 0 and j == 0:
                continue
            best, b = INF, None
            if i > 0:
                v = dp[i - 1][j] + GAP
                if v < best:
                    best, b = v, (i - 1, j)
            if j > 0:
                v = dp[i][j - 1] + GAP
                if v < best:
                    best, b = v, (i, j - 1)
            if i > 0 and j > 0:
                v = dp[i - 1][j - 1] + abs(Ls[i - 1] / ms - Lt[j - 1] / mt)
                if v < best:
                    best, b = v, (i - 1, j - 1)
            dp[i][j] = best
            bk[i][j] = b
    # 回溯：每個原文段取「匹配到」的譯文索引；未匹配則取最近
    mapping = [None] * n
    i, j = n, m
    while i > 0 or j > 0:
        pi, pj = bk[i][j]
        if pi == i - 1 and pj == j - 1:
            mapping[i - 1] = j - 1
        elif pi == i - 1:
            mapping[i - 1] = max(0, j - 1)
        i, j = pi, pj
    last = 0
    for k in range(n):
        if mapping[k] is None:
            mapping[k] = last
        mapping[k] = max(mapping[k], last)
        last = mapping[k]
    return mapping


res = {}
for f in sorted(os.listdir(S)):
    if not f.endswith('.txt'):
        continue
    k = f[:-4]
    sp = [x for x in io.open(os.path.join(S, f), encoding='utf-8').read().split('\n')[5:] if x.strip()]
    tt = [x for x in re.split(r'\r?\n\r?\n', io.open(os.path.join(T, k + '.txt'), encoding='utf-8').read()) if x.strip()]
    if not sp or not tt:
        continue
    Ls = [max(1, han(x)) for x in sp]
    Lt = [max(1, han(x)) for x in tt]
    mp = align(Ls, Lt)
    res[k] = mp
json.dump(res, io.open(OUT, 'w', encoding='utf-8'), ensure_ascii=False)
print('分塊', len(res))
for k in list(res)[:4]:
    print(' ', k, '原文', len(res[k]), '對應譯文前10', res[k][:10])
