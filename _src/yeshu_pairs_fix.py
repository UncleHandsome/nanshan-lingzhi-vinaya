# -*- coding: utf-8 -*-
"""修正業疏「逐 chunk 旋轉位移」：每個 chunk 的譯文其實是「前一 chunk 尾巴 + 本 chunk 開頭」。

作法：
  1. 以長度相關性求每個 chunk 的位移 k（src[0] ↔ tr[-k]）。
  2. 本 chunk 的完整譯文 = out[i][-k:] + out[i+1][:-k]（尾巴不足時向後借）。
  3. 輸出 AI語譯/_work/ys_pairs_fixed.json：{chunk: [[src, tr], ...]}
"""
import os, io, re, glob, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
SD = os.path.join(B, 'TXT_分卷_標點', '03_業疏')
TD = os.path.join(B, 'AI語譯', 'out', '03_業疏')
OUT = os.path.join(B, 'AI語譯', '_work', 'ys_pairs_fixed.json')
RANGE = 100


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


def best_offset(src, tr):
    best = (-9, 0)
    for k in range(-RANGE, RANGE + 1):
        c = corr(src[k:], tr) if k >= 0 else corr(src, tr[-k:])
        if c > best[0]:
            best = (c, k)
    return best[1], best[0]



ANCH = re.compile(r'「([^」]{2,20})」|《([^》]{1,20})》')


def anchors(s):
    return [a or b for a, b in ANCH.findall(s or '') if (a or b)]


def anchor_score(src, tr, k):
    n = min(len(src), len(tr))
    hit = tot = 0
    for i in range(n):
        j = i + k
        if j < 0 or j >= len(tr):
            continue
        aa = anchors(tr[j])
        if not aa:
            continue
        tot += len(aa)
        hit += sum(1 for a in aa if a in src[i])
    return hit, tot


def best_offset2(src, tr):
    lens_s = [len(x) for x in src]
    lens_t = [len(x) for x in tr]
    cand = []
    for k in range(-RANGE, RANGE + 1):
        c = corr(lens_s[k:], lens_t) if k >= 0 else corr(lens_s, lens_t[-k:])
        cand.append((c, k))
    cand.sort(reverse=True)
    best = None
    for c, k in cand[:6]:
        hit, tot = anchor_score(src, tr, k)
        sc = (hit / tot) if tot >= 5 else -1
        key = (sc, c)
        if best is None or key > best[0]:
            best = (key, k, c, sc)
    return best[1], best[2], best[3]

def main():
    chunks = []
    for f in sorted(glob.glob(os.path.join(SD, '*.txt'))):
        ch = os.path.splitext(os.path.basename(f))[0]
        chunks.append((ch, load(f), load(os.path.join(TD, ch + '.txt'))))

    offs = []
    for ch, src, tr in chunks:
        k, c, asc = best_offset2(src, tr)
        offs.append((k, c))
    result = {}
    stats = []
    for i, (ch, src, tr) in enumerate(chunks):
        k, c = offs[i]
        shift = -k                      # 本 chunk 內容在 out 中的起始索引
        own = tr[shift:] if shift > 0 else tr[:]
        need = len(src) - len(own)
        j = i + 1
        while need > 0 and j < len(chunks):
            nxt = chunks[j][2]
            k2 = -offs[j][0]
            avail = nxt[:k2] if k2 > 0 else nxt
            take = avail[:need]
            own = own + take
            need -= len(take)
            j += 1
        if len(own) < len(src):
            own = own + [''] * (len(src) - len(own))
        result[ch] = [[src[n], own[n]] for n in range(len(src))]
        stats.append((ch, len(src), shift, round(c, 2), sum(1 for t in own[:len(src)] if t)))

    with io.open(OUT, 'w', encoding='utf-8') as fh:
        json.dump(result, fh, ensure_ascii=False)
    print('chunks', len(result), 'pairs', sum(len(v) for v in result.values()))
    for s in stats[:12]:
        print(s)
    print('→', OUT)


if __name__ == '__main__':
    main()
