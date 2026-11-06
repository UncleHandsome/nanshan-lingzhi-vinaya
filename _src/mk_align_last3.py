# -*- coding: utf-8 -*-
"""最後三篇（28-30）的 AI 對齊批次"""
import io, os, re, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
OUT = os.path.join(B, 'AI語譯', '_work', 'align_last3')
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

Z2S = [0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 8, 9, 10, 11, 12, 13, 13, 13,
       14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29]
zj = []
for k, sp, tt in load('資持記_細分', '資持記'):
    zj += list(zip(sp, tt))
ZP = re.compile(r'釋([\u4e00-\u9fff]{2,6})篇')
zs, z = [], None
for o, tt in zj:
    m = ZP.search(o) or ZP.search(tt)
    if m:
        z = []
        zs.append(z)
    if z is not None:
        z.append(o)


def zitems_for(idx):
    out = []
    for i, sec in enumerate(zs):
        if i < len(Z2S) and Z2S[i] == idx:
            out += sec
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        os.remove(os.path.join(OUT, f))
    n = 0
    for idx in (27, 28, 29):
        zi = zitems_for(idx)
        C = secs[idx]['items']
        if not zi or not C:
            print('skip', idx + 1, len(zi), len(C))
            continue
        n += 1
        io.open(os.path.join(OUT, '%03d.json' % n), 'w', encoding='utf-8').write(json.dumps(dict(
            sec=idx + 1, name=secs[idx]['name'],
            items=[dict(z=i, text=x[:80]) for i, x in enumerate(zi)],
            cand=[dict(c=c, text=x[:80]) for c, x in enumerate(C)]), ensure_ascii=False, indent=1))
        print('batch', n, '篇', idx + 1, secs[idx]['name'], '記', len(zi), '鈔', len(C))
    print('batches', n)


if __name__ == '__main__':
    main()
