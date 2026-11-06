# -*- coding: utf-8 -*-
"""產生 AI 對齊批次：每個批次 60 個記段 + 其前後約 28 個鈔段（依字數比例定位視窗）。"""
import io, os, re, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
OUT = os.path.join(B, 'AI語譯', '_work', 'align_ai')
han = lambda s: ''.join(re.findall(r'[\u4e00-\u9fff]', s))
BLOCK = 150
PAD_BACK, PAD_FWD = 10, 45


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
Z2S = [0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 8, 9, 10, 11, 12, 13, 13, 13,
       14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29]


def sections():
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
                cur['items'].append(o)
    return secs


def zsecs():
    zj = []
    for k, sp, tt in load('資持記_細分', '資持記'):
        zj += sp
    ZP = re.compile(r'釋([\u4e00-\u9fff]{2,6})篇')
    zs, z = [], None
    for o in zj:
        m = ZP.search(o)
        if m:
            z = []
            zs.append(z)
        if z is not None:
            z.append(o)
    return zs


def main():
    secs = sections()
    zs = zsecs()
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        os.remove(os.path.join(OUT, f))
    n = 0
    manifest = []
    for idx, sec in enumerate(secs):
        zi = []
        for k, z in enumerate(zs):
            if k < len(Z2S) and Z2S[k] == idx:
                zi += z
        C = sec['items']
        if not C or not zi:
            continue
        clen = [max(1, len(han(x))) for x in C]
        zlen = [max(1, len(han(x))) for x in zi]
        tc, tz = float(sum(clen)), float(sum(zlen))
        cum_c, acc = [], 0.0
        for L in clen:
            acc += L
            cum_c.append(acc / tc)
        for s in range(0, len(zi), BLOCK):
            block = zi[s:s + BLOCK]
            zpos = sum(zlen[:s]) / tz
            # 視窗前後留白
            lo = 0
            for j, cpos in enumerate(cum_c):
                if cpos <= zpos:
                    lo = j
            hi = lo + 1
            target = (sum(zlen[:s + len(block)]) / tz)
            while hi < len(C) and cum_c[hi - 1] < target:
                hi += 1
            lo = max(0, lo - PAD_BACK)
            hi = min(len(C), hi + PAD_FWD)
            n += 1
            f = '%03d.json' % n
            io.open(os.path.join(OUT, f), 'w', encoding='utf-8').write(json.dumps(dict(
                sec=idx + 1, name=sec['name'], z_from=s, z_to=s + len(block) - 1,
                items=[dict(z=s + i, text=x[:70]) for i, x in enumerate(block)],
                cand=[dict(c=c, text=C[c][:70]) for c in range(lo, hi)]
            ), ensure_ascii=False, indent=1))
            manifest.append(dict(file=f, sec=idx + 1, z_from=s, z_to=s + len(block) - 1))
    io.open(os.path.join(OUT, 'manifest.json'), 'w', encoding='utf-8').write(json.dumps(manifest, ensure_ascii=False))
    print('batches', n)


if __name__ == '__main__':
    main()
