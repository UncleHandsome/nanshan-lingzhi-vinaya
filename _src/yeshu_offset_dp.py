# -*- coding: utf-8 -*-
"""業疏偏移量：全域 DP（長度相關 + 引文命中 + 平滑懲罰）。

模型：out_chunk[j] 是 src_chunk[j+k] 的譯文。
分數 = 0.6*長度相關 + 0.4*引文命中率，並懲罰相鄰 chunk 的 k 跳動。
"""
import os, io, re, glob, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
SD = os.path.join(B, 'TXT_分卷_標點', '03_業疏')
TD = os.path.join(B, 'AI語譯', 'out', '03_業疏')
RANGE = 100
LAM = 0.06
ANCH = re.compile(r'「([^」]{2,20})」|《([^》]{1,20})》')


def load(p):
    return [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(p, encoding='utf-8').read()) if x.strip()]


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


def anchors(s):
    return [a or b for a, b in ANCH.findall(s or '') if (a or b)]


def score(src, tr, k):
    ls = [len(x) for x in src]
    lt = [len(x) for x in tr]
    c = corr(ls[k:], lt) if k >= 0 else corr(ls, lt[-k:])
    if c < -1:
        c = 0
    hit = tot = 0
    n = min(len(src) - max(0, k), len(tr) - max(0, -k))
    for i in range(n):
        t = tr[i + max(0, -k)] if k < 0 else tr[i]
        s = src[i + max(0, k)]
        aa = anchors(t)
        if not aa:
            continue
        tot += len(aa)
        hit += sum(1 for a in aa if a in s)
    a = hit / tot if tot >= 8 else 0
    return 0.6 * max(0, c) + 0.4 * a, c, a


def main():
    chunks = []
    for f in sorted(glob.glob(os.path.join(SD, '*.txt'))):
        ch = os.path.splitext(os.path.basename(f))[0]
        chunks.append((ch, load(f), load(os.path.join(TD, ch + '.txt'))))

    ks = list(range(-RANGE, RANGE + 1))
    table = []
    for ch, src, tr in chunks:
        table.append({k: score(src, tr, k) for k in ks})

    # DP
    dp = [dict() for _ in chunks]
    back = [dict() for _ in chunks]
    for k in ks:
        dp[0][k] = table[0][k][0]
        back[0][k] = 0
    for i in range(1, len(chunks)):
        prev = dp[i - 1]
        for k in ks:
            best = None
            for k0, v in prev.items():
                s = v - LAM * abs(k - k0)
                if best is None or s > best[0]:
                    best = (s, k0)
            dp[i][k] = best[0] + table[i][k][0]
            back[i][k] = best[1]
    k = max(dp[-1], key=dp[-1].get)
    path = [k]
    for i in range(len(chunks) - 1, 0, -1):
        k = back[i][k]
        path.append(k)
    path.reverse()

    out = []
    for i, (ch, src, tr) in enumerate(chunks):
        k = path[i]
        s, c, a = table[i][k]
        out.append(dict(chunk=ch, k=k, score=round(s, 3), corr=round(c, 2), anchor=round(a, 2)))

    json.dump(out, io.open(os.path.join(B, 'AI語譯', '_work', 'ys_offsets_dp.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    for r in out:
        print('%-16s k=%4d  score=%.2f  corr=%.2f  anchor=%.2f' % (r['chunk'], r['k'], r['score'], r['corr'], r['anchor']))


if __name__ == '__main__':
    main()
