# -*- coding: utf-8 -*-
"""篇內對齊：以 5-gram 錨定，其餘在錨點間內插；輸出 hb_align.json"""
import io, os, re, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
han = lambda s: ''.join(re.findall(r'[\u4e00-\u9fff]', s))
N = 5


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
secs, cur = [], None
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

Z2S = [0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 8, 9, 10, 11, 12, 13, 13, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29]
zj = []
for k, sp, tt in load('資持記_細分', '資持記'):
    for i, o in enumerate(sp):
        zj.append((o, tt[i] if i < len(tt) else ''))
ZP = re.compile(r'釋([\u4e00-\u9fff]{2,6})篇')
zsecs, z = [], None
for o, t in zj:
    m = ZP.search(t) or ZP.search(o)
    if m:
        z = dict(name=m.group(1), items=[])
        zsecs.append(z)
    if z is not None:
        z['items'].append((o, t))


def grams(s, n=N):
    h = han(s)
    return [h[i:i + n] for i in range(max(0, len(h) - n + 1))]


out = {}
tot = hit = 0
for idx, sec in enumerate(secs):
    zi = []
    for i, zs in enumerate(zsecs):
        if i < len(Z2S) and Z2S[i] == idx:
            zi += zs['items']
    C = [han(o) for o, t in sec['items']]
    pos = {}
    for j, c in enumerate(C):
        for p in range(max(0, len(c) - N + 1)):
            pos.setdefault(c[p:p + N], []).append((j, p))
    assigned = []
    for o, t in zi:
        gs = grams(o)
        cand = []
        for g in gs:
            for j, p in pos.get(g, [])[:3]:
                cand.append(j)
        if cand:
            cand.sort()
            assigned.append(cand[len(cand) // 2])
            hit += 1
        else:
            assigned.append(None)
        tot += 1
    ks = [k for k, v in enumerate(assigned) if v is not None]
    if ks:
        for k in range(len(assigned)):
            if assigned[k] is not None:
                continue
            prev = max([x for x in ks if x < k], default=None)
            nxt = min([x for x in ks if x > k], default=None)
            if prev is None:
                assigned[k] = assigned[nxt]
            elif nxt is None:
                assigned[k] = assigned[prev]
            else:
                frac = (k - prev) / (nxt - prev)
                assigned[k] = int(round(assigned[prev] + frac * (assigned[nxt] - assigned[prev])))
    last = 0
    for k in range(len(assigned)):
        if assigned[k] is None:
            assigned[k] = last
        assigned[k] = max(last, assigned[k])
        last = assigned[k]
    out[str(idx)] = assigned

print('記段', tot, '有 %d-gram 錨點 %d (%.1f%%)' % (N, hit, 100.0 * hit / max(1, tot)))
json.dump(out, io.open(os.path.join(B, 'AI語譯', '_work', 'hb_align.json'), 'w', encoding='utf-8'), ensure_ascii=False)
print('saved hb_align.json')
