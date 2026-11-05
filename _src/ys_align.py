# -*- coding: utf-8 -*-
"""Banded monotone alignment of 業疏 translations to source lines.

Prints the alignment for selected chunks so we can judge whether the
translation stream is a re-segmentation of the same text.
"""
import os, io, re, sys, json
import numpy as np

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
CJK = re.compile(r'[\u4e00-\u9fff]')


def bigrams(s):
    s = ''.join(CJK.findall(s))
    return set(s[i:i + 2] for i in range(len(s) - 1))


def load():
    S = os.path.join(B, 'TXT_分卷', '03_業疏')
    T = os.path.join(B, 'AI語譯', 'out', '03_業疏')
    keys = [f[:-4] for f in sorted(os.listdir(S), key=lambda x: (0 if x.startswith('00_') else 1, x)) if f.endswith('.txt')]
    src, tr, bounds = [], [], []
    for k in keys:
        sp = [x.strip() for x in io.open(os.path.join(S, k + '.txt'), encoding='utf-8').read().split('\n')[5:] if x.strip()]
        tp = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(os.path.join(T, k + '.txt'), encoding='utf-8').read()) if x.strip()]
        bounds.append((k, len(src), len(src) + len(sp)))
        src += sp
        tr += tp
    return keys, src, tr, bounds


def main():
    keys, src, tr, bounds = load()
    n, m = len(src), len(tr)
    print('src', n, 'tr', m, 'chunks', len(bounds), file=sys.stderr)
    SB = [bigrams(x) for x in src]
    TB = [bigrams(x) for x in tr]
    Ls = np.array([len(x) for x in src], dtype=np.float64)
    Lt = np.array([len(x) for x in tr], dtype=np.float64)
    BAND = 90
    SKIP = 0.045

    # sim matrix on band
    NEG = -9.0
    sim = np.full((n, BAND * 2 + 1), NEG)
    for i in range(n):
        lo = max(0, i - BAND)
        hi = min(m, i + BAND + 1)
        a = SB[i]
        la = len(a)
        for j in range(lo, hi):
            b = TB[j]
            if not b or not la:
                continue
            ov = len(a & b)
            if not ov:
                continue
            s = ov / ((la ** 0.5) * (len(b) ** 0.5))
            # length ratio bonus
            lr = abs(np.log((Ls[i] + 8) / (Lt[j] + 8)))
            sim[i, j - lo] = s - 0.05 * lr

    D = np.full((n + 1, BAND * 2 + 1), -1e9)
    # state: (i, offset j-i)
    def off(j, i):
        return j - i + BAND

    D[0, BAND] = 0.0
    PTR = np.zeros((n + 1, BAND * 2 + 1), dtype=np.int8)
    for i in range(n):
        for o in range(2 * BAND + 1):
            cur = D[i, o]
            if cur <= -1e8:
                continue
            j = i + o - BAND
            # 1:1
            if 0 <= j < m and sim[i, o] > NEG:
                v = cur + sim[i, o]
                if v > D[i + 1, o]:
                    D[i + 1, o] = v; PTR[i + 1, o] = 1
            # skip source
            v = cur - SKIP
            if v > D[i + 1, o]:
                D[i + 1, o] = v; PTR[i + 1, o] = 2
            # skip translation
            if 0 <= j < m and o - 1 >= 0:
                v = cur - SKIP
                if v > D[i, o - 1]:
                    D[i, o - 1] = v; PTR[i, o - 1] = 3

    # traceback from best end
    end_offsets = [o for o in range(2 * BAND + 1) if D[n, o] > -1e8]
    best_o = max(end_offsets, key=lambda o: D[n, o] - SKIP * abs(n + o - BAND - m))
    mapping = {}
    i, o = n, best_o
    while i > 0:
        p = PTR[i, o]
        if p == 1:
            mapping[i - 1] = i + o - BAND - 1
            i -= 1
        elif p == 2:
            i -= 1
        elif p == 3:
            o += 1
        else:
            i -= 1
    print('mapped', len(mapping), 'score', round(D[n, best_o], 1), file=sys.stderr)
    json.dump({str(k): v for k, v in mapping.items()}, io.open(os.path.join(B, 'AI語譯', '_work', 'ys_map.json'), 'w', encoding='utf-8'))

    # diagnostics per chunk
    for key, a, b in bounds:
        ds = []
        for i in range(a, b):
            if i in mapping:
                ds.append(mapping[i] - i)
        if not ds:
            continue
        med = sorted(ds)[len(ds) // 2]
        dev = [d - med for d in ds]
        ok = sum(1 for d in dev if abs(d) <= 2)
        if ok < len(ds) * 0.75 or abs(med) > 3:
            print('%-16s n=%3d med=%+3d ok=%3d%%' % (key, len(ds), med, round(100 * ok / len(ds))))


if __name__ == '__main__':
    main()
