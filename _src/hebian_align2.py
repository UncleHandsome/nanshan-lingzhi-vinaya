# -*- coding: utf-8 -*-
"""以 4-gram 相似度 + 單調 DP 將《資持記》每段對到《行事鈔》段。"""
import io, os, re, json
import numpy as np

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
han = lambda s: ''.join(re.findall(r'[\u4e00-\u9fff]', s))


def load(src, tr):
    S = os.path.join(B, 'TXT_分卷', src)
    T = os.path.join(B, 'AI語譯', 'out', tr)
    out = []
    for f in sorted(os.listdir(S), key=lambda x: (0 if x.startswith('00_') else 1, x)):
        if not f.endswith('.txt'):
            continue
        k = f[:-4]
        tp = os.path.join(T, k + '.txt')
        if not os.path.exists(tp):
            continue
        sp = [x.strip() for x in io.open(os.path.join(S, f), encoding='utf-8').read().split('\n')[5:] if x.strip()]
        tt = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(tp, encoding='utf-8').read()) if x.strip()]
        out.append((k, sp, tt))
    return out


PATS = re.compile(r'^([\u4e00-\u9fff]{2,8})篇第([一二三四五六七八九十]+)$')
PATS2 = re.compile(r'^\d+\s*[\u4e00-\u9fff]{2,10}篇\(上[一二三四五六七八九十]?\)$')


def sections():
    secs = []
    cur = None
    for k, sp, tt in load('01_行事鈔', '01_行事鈔'):
        for i, o in enumerate(sp):
            if PATS2.match(o.strip()):
                continue
            m = PATS.match(o)
            if m:
                if any(x['no'] == m.group(2) for x in secs):
                    cur = next(x for x in secs if x['no'] == m.group(2))
                else:
                    cur = dict(name=m.group(1), no=m.group(2), items=[])
                    secs.append(cur)
                continue
            if cur is not None:
                cur['items'].append((o, tt[i] if i < len(tt) else ''))
    return secs


def zsections():
    zflat = []
    for k, sp, tt in load('資持記_細分', '資持記'):
        for i, o in enumerate(sp):
            zflat.append((o, tt[i] if i < len(tt) else ''))
    ZP = re.compile(r'釋([\u4e00-\u9fff]{2,6})篇')
    zs = []
    z = None
    for o, t in zflat:
        m = ZP.search(t) or ZP.search(o)
        if m:
            z = dict(name=m.group(1), items=[])
            zs.append(z)
        if z is not None:
            z['items'].append((o, t))
    return zs


def grams(s, n=4):
    h = han(s)
    return set(h[i:i + n] for i in range(max(0, len(h) - n + 1)))


def align(sec, zi):
    if not zi or not sec['items']:
        return [0] * len(zi)
    C = [grams(o) for o, t, *_ in [(o, t) for o, t in sec['items']]]
    Z = [grams(o) for o, t in zi]
    n, m = len(Z), len(C)
    sim = np.zeros((n, m), dtype=np.float32)
    for i in range(n):
        if not Z[i]:
            continue
        for j in range(m):
            if not C[j]:
                continue
            inter = len(Z[i] & C[j])
            if inter:
                sim[i, j] = inter / (len(Z[i]) ** 0.5 * len(C[j]) ** 0.5)
    dp = np.zeros((n + 1, m + 1), dtype=np.float32)
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            best = max(dp[i - 1, j], dp[i, j - 1], dp[i - 1, j - 1] + sim[i - 1, j - 1])
            dp[i, j] = best
    i, j = n, m
    path = [0] * n
    while i > 0:
        if j > 0 and abs(dp[i, j] - (dp[i - 1, j - 1] + sim[i - 1, j - 1])) < 1e-6:
            path[i - 1] = j - 1
            i -= 1
            j -= 1
        elif dp[i, j] == dp[i - 1, j]:
            path[i - 1] = max(0, j - 1)
            i -= 1
        else:
            path[i - 1] = max(0, j - 1)
            j -= 1
    return path


def main():
    secs = sections()
    zs = zsections()
    out = {}
    tot = hit = 0
    for idx, sec in enumerate(secs):
        zi = zs[idx]['items'] if idx < len(zs) else []
        path = align(sec, zi)
        out[str(idx)] = path
        # 統計：有多少記段真的與所對鈔段有 4-gram 交集
        for k, (o, t) in enumerate(zi):
            tot += 1
            if path and (grams(o) & grams(sec['items'][path[k]][0])):
                hit += 1
    print('篇', len(secs), '記段', tot, '對到有交集 %.1f%%' % (100.0 * hit / max(1, tot)))
    json.dump(out, io.open(os.path.join(B, 'AI語譯', '_work', 'hb_align.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    print('saved')


if __name__ == '__main__':
    main()
