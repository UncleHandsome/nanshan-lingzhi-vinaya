# -*- coding: utf-8 -*-
"""業疏：全書單調對齊（帶狀 DP），輸出 ys_tt_align.json"""
import io, os, re, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
S = os.path.join(B, 'TXT_分卷', '03_業疏')
T = os.path.join(B, 'AI語譯', 'out', '03_業疏')
OUT = os.path.join(B, 'AI語譯', '_work', 'ys_tt_align.json')
han = lambda s: ''.join(re.findall(r'[\u4e00-\u9fff]', s))


def grams(s, n=2):
    h = han(s)
    return set(h[i:i + n] for i in range(max(0, len(h) - n + 1)))


def main():
    SP, TT, keys = [], [], []
    for f in sorted(os.listdir(S)):
        if not f.endswith('.txt'):
            continue
        k = f[:-4]
        sp = [x.strip() for x in io.open(os.path.join(S, f), encoding='utf-8').read().split('\n')[5:] if x.strip()]
        tt = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(os.path.join(T, k + '.txt'), encoding='utf-8').read()) if x.strip()]
        for x in sp:
            SP.append(x)
            keys.append(k)
        TT += tt
    n, m = len(SP), len(TT)
    print('SP', n, 'TT', m)
    G1 = [grams(x) for x in SP]
    G2 = [grams(x) for x in TT]
    L1 = [max(1, len(han(x))) for x in SP]
    L2 = [max(1, len(han(x))) for x in TT]

    BAND = 80
    NEG = -1e9
    # dp[j] 只在帶內；用前一行字典存
    prev = {0: 0.0}
    back = []
    for i in range(n):
        cur = {}
        row = {}
        jlo = max(0, i - BAND)
        jhi = min(m, i + BAND + 1)
        for j in range(jlo, jhi):
            best, bp = NEG, None
            for dj in (0, -1):
                pj = j - dj
                if pj in prev:
                    v = prev[pj]
                    if v > best:
                        best, bp = v, pj
            if best <= NEG / 2:
                continue
            a, b = G1[i], G2[j]
            sim = len(a & b) / float(max(1, min(len(a), len(b))))
            ratio = min(L1[i], L2[j]) / float(max(L1[i], L2[j]))
            sc = best + sim + 0.15 * ratio
            cur[j] = sc
            row[j] = bp
        if not cur:
            break
        prev = cur
        back.append(row)
    # 回溯
    if not prev:
        print('no path')
        return
    j = max(prev, key=prev.get)
    mapping = [-1] * n
    for i in range(n - 1, -1, -1):
        mapping[i] = j
        if i < len(back):
            j = back[i].get(j, back[i].get(j - 1, 0))
        if j < 0:
            j = 0
    json.dump(dict(keys=keys, map=mapping), io.open(OUT, 'w', encoding='utf-8'), ensure_ascii=False)
    good = sum(1 for i, j2 in enumerate(mapping) if 0 <= j2 < m)
    print('mapped', good, '/', n)
    for i in (0, 1, 2, 1348, 3000):
        if i < n:
            j2 = mapping[i]
            print('SP%d %s' % (i, SP[i][:34]))
            print('  TT%d %s' % (j2, TT[j2][:34] if 0 <= j2 < m else '-'))


if __name__ == '__main__':
    main()
