# -*- coding: utf-8 -*-
"""業疏：偵測每個 chunk 的譯文位移量（分卷段 i ↔ 譯文段 i+k）。"""
import os, io, re, glob

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
SD = os.path.join(B, 'TXT_分卷_標點', '03_業疏')
TD = os.path.join(B, 'AI語譯', 'out', '03_業疏')
RANGE = 90


def load(p, split=True):
    t = io.open(p, encoding='utf-8').read()
    if split:
        return [x.strip() for x in re.split(r'\r?\n\r?\n', t) if x.strip()]
    return [x.strip() for x in t.split('\n')[5:] if x.strip()]


def corr(a, b):
    n = min(len(a), len(b))
    if n < 15:
        return -9
    xs, ys = a[:n], b[:n]
    mx, my = sum(xs) / n, sum(ys) / n
    sx = sum((x - mx) ** 2 for x in xs) ** .5
    sy = sum((y - my) ** 2 for y in ys) ** .5
    if sx == 0 or sy == 0:
        return 0
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (sx * sy)


def main():
    rows = []
    for f in sorted(glob.glob(os.path.join(SD, '*.txt'))):
        ch = os.path.splitext(os.path.basename(f))[0]
        src = [len(x) for x in load(f)]
        tp = os.path.join(TD, ch + '.txt')
        tr = [len(x) for x in load(tp)]
        best = (-9, 0)
        for k in range(-RANGE, RANGE + 1):
            if k >= 0:
                c = corr(src[k:], tr)
            else:
                c = corr(src, tr[-k:])
            if c > best[0]:
                best = (c, k)
        rows.append((ch, len(src), len(tr), best[1], round(best[0], 2)))
    ok = sum(1 for r in rows if r[3] == 0)
    print('%-16s %5s %5s %5s %6s' % ('chunk', 'src', 'tr', 'off', 'corr'))
    for r in rows:
        print('%-16s %5d %5d %5d %6.2f' % r)
    print('\n位移=0：%d/%d' % (ok, len(rows)))


if __name__ == '__main__':
    main()
