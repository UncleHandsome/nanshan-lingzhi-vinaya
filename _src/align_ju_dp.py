# -*- coding: utf-8 -*-
"""句讀行 → 分卷段 的單調對齊（長度 DP），輸出 ys_ju_map.json"""
import io, os, re, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
S = os.path.join(B, 'TXT_分卷', '03_業疏')
J = os.path.join(B, 'TXT_句讀', '03_業疏')
OUT = os.path.join(B, 'AI語譯', '_work', 'ys_ju_map.json')
han = lambda s: len(re.findall(r'[\u4e00-\u9fff]', s))
SKIP = ('=', '.', '四分律', '（', '南山三大部', '底本')


def align(Lj, Ls):
    n, m = len(Lj), len(Ls)
    if not n or not m:
        return []
    mj = sum(Lj) / n
    ms = sum(Ls) / m
    INF = 1e9
    dp = [[INF] * (m + 1) for _ in range(n + 1)]
    bk = [[None] * (m + 1) for _ in range(n + 1)]
    dp[0][0] = 0
    for i in range(n + 1):
        for j in range(m + 1):
            if i == 0 and j == 0:
                continue
            best, b = INF, None
            if i:
                v = dp[i - 1][j] + 0.35
                if v < best:
                    best, b = v, (i - 1, j)
            if j:
                v = dp[i][j - 1] + 0.05
                if v < best:
                    best, b = v, (i, j - 1)
            if i and j:
                v = dp[i - 1][j - 1] + abs(Lj[i - 1] / mj - Ls[j - 1] / ms)
                if v < best:
                    best, b = v, (i - 1, j - 1)
            dp[i][j] = best
            bk[i][j] = b
    mp = [0] * n
    i, j = n, m
    while i > 0 or j > 0:
        pi, pj = bk[i][j]
        if pi == i - 1 and pj == j - 1:
            mp[i - 1] = j - 1
        elif pi == i - 1:
            mp[i - 1] = max(0, j - 1)
        i, j = pi, pj
    last = 0
    for k in range(n):
        mp[k] = max(mp[k], last)
        last = mp[k]
    return mp


res = {}
for f in sorted(os.listdir(S)):
    if not f.endswith('.txt'):
        continue
    k = f[:-4]
    jp = os.path.join(J, k + '.txt')
    if not os.path.exists(jp):
        continue
    sp = [x.strip() for x in io.open(os.path.join(S, f), encoding='utf-8').read().split('\n')[5:] if x.strip()]
    ju = [x.strip() for x in io.open(jp, encoding='utf-8').read().split('\n') if x.strip()]
    while ju and (len(ju[0]) < 8 or ju[0].startswith(SKIP)):
        ju = ju[1:]
    if not sp or not ju:
        continue
    res[k] = align([max(1, han(x)) for x in ju], [max(1, han(x)) for x in sp])
json.dump(res, io.open(OUT, 'w', encoding='utf-8'), ensure_ascii=False)
print('分塊', len(res))
for k in list(res)[:3]:
    print(' ', k, '句讀', len(res[k]), '首 8 個對應段', res[k][:8])
