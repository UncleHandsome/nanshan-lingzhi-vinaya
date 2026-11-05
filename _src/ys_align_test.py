# -*- coding: utf-8 -*-
"""Test global monotone alignment of 業疏 translation stream to source lines.

Both sequences have equal length (5185). If the translation stream is a
re-segmentation of the same text, a monotone DP on (log length ratio) should
recover a near-diagonal mapping.
"""
import os, io, re, sys, math
import numpy as np

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
TAG, SD = '03_業疏', '03_業疏'


def chunks():
    S = os.path.join(B, 'TXT_分卷', SD)
    T = os.path.join(B, 'AI語譯', 'out', TAG)
    files = sorted(os.listdir(S), key=lambda x: (0 if x.startswith('00_') else 1, x))
    out = []
    for f in files:
        if not f.endswith('.txt'):
            continue
        key = f[:-4]
        sp = [x.strip() for x in io.open(os.path.join(S, f), encoding='utf-8').read().split('\n')[5:] if x.strip()]
        tp = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(os.path.join(T, key + '.txt'), encoding='utf-8').read()) if x.strip()]
        out.append((key, sp, tp))
    return out


def main():
    C = chunks()
    src = []
    tr = []
    bounds = []  # (key, src_start, src_end)
    s = t = 0
    for key, sp, tp in C:
        src += sp
        tr += tp
        bounds.append((key, s, s + len(sp), t, t + len(tp)))
        s += len(sp)
        t += len(tp)
    n, m = len(src), len(tr)
    print('src', n, 'tr', m)

    Ls = np.array([len(x) for x in src], dtype=np.float64)
    Lt = np.array([len(x) for x in tr], dtype=np.float64)
    # cost on log-length difference, normalized
    cost = np.abs(np.log((Ls[:, None] + 4) / (Lt[None, :] + 4)))

    # DP: monotone alignment allowing 1:1, 1:0, 0:1 with skip penalty
    INF = 1e9
    D = np.full((n + 1, m + 1), INF)
    P = np.zeros((n + 1, m + 1), dtype=np.int8)
    D[0, :] = np.arange(m + 1) * 0.55
    D[:, 0] = np.arange(n + 1) * 0.55
    P[0, 1:] = 3  # from left
    P[1:, 0] = 2  # from up
    for i in range(1, n + 1):
        ci = cost[i - 1]
        prev = D[i - 1]
        cur = D[i]
        for j in range(1, m + 1):
            best = prev[j - 1] + ci[j - 1]
            bp = 1
            up = prev[j] + 0.55
            if up < best:
                best = up; bp = 2
            left = cur[j - 1] + 0.55
            if left < best:
                best = left; bp = 3
            cur[j] = best
            P[i, j] = bp
    # traceback
    mapping = {}
    i, j = n, m
    while i > 0 or j > 0:
        p = P[i, j]
        if p == 1:
            mapping[i - 1] = j - 1
            i -= 1; j -= 1
        elif p == 2:
            i -= 1
        else:
            j -= 1
    print('mapped', len(mapping), 'of', n)
    # report per chunk offsets
    tot_bad = 0
    for key, s0, s1, t0, t1 in bounds:
        ds = [mapping[i] - i - (t0 - s0) for i in range(s0, s1) if i in mapping]
        if not ds:
            print(key, 'unmapped'); continue
        # dominant offset relative to t0-s0
        from collections import Counter
        c = Counter(ds)
        dom, cnt = c.most_common(1)[0]
        dev = [d - dom for d in ds]
        ok = sum(1 for d in dev if abs(d) <= 1)
        tot_bad += len(ds) - ok
        if cnt < len(ds) * 0.8 or ok < len(ds) * 0.8:
            print('%-16s n=%3d dom=%+3d (%2d) ok=%.0f%%' % (key, len(ds), dom, cnt, 100.0 * ok / len(ds)))
    print('total deviating', tot_bad)
    np.save(os.path.join(B, 'AI語譯', '_work', 'ys_map.npy'), np.array([mapping.get(i, -1) for i in range(n)]))


if __name__ == '__main__':
    main()
