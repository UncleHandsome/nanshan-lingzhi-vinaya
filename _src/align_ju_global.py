# -*- coding: utf-8 -*-
"""尼鈔／義鈔：用長度 DP 把句讀段落分配到分卷段落"""
import io, os, re, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
han = lambda s: len(re.findall(r'[\u4e00-\u9fff]', s))
TARGETS = [('04_比丘尼鈔', '04_四分律比丘尼鈔_句讀_clean.txt', 'nicao_ju_map.json'),
           ('05_拾毗尼義鈔', '05_四分律拾毗尼義鈔_句讀_clean.txt', 'yichao_ju_map.json')]
GAP = 0.35


def align(Lj, Ls):
    n, m = len(Lj), len(Ls)
    mj = sum(Lj) / max(1, n)
    ms = sum(Ls) / max(1, m)
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
                v = dp[i - 1][j] + GAP
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


for src, jufile, out in TARGETS:
    S = os.path.join(B, 'TXT_分卷', src)
    sp_all = []
    for f in sorted(os.listdir(S), key=lambda x: (0 if x.startswith('00_') else 1, x)):
        if not f.endswith('.txt'):
            continue
        sp = [x.strip() for x in io.open(os.path.join(S, f), encoding='utf-8').read().split('\n')[5:] if x.strip()]
        sp_all += sp
    ju = [x.strip() for x in re.split(r'\n\s*\n', io.open(os.path.join(B, jufile), encoding='utf-8').read()) if x.strip()]
    print(src, 'sp', len(sp_all), 'ju', len(ju))
    mp = align([max(1, han(x)) for x in ju], [max(1, han(x)) for x in sp_all])
    buckets = {}
    for li, si in enumerate(mp):
        buckets.setdefault(si, []).append(li)
    json.dump({'sp': len(sp_all), 'ju': len(ju), 'map': mp},
              io.open(os.path.join(B, 'AI語譯', '_work', out), 'w', encoding='utf-8'), ensure_ascii=False)
    print('  →', out, '覆蓋 sp', len(buckets), '/', len(sp_all))
