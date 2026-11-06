# -*- coding: utf-8 -*-
"""用段落長度相關性求每塊位移（可為負），輸出 ys_offsets_final.json"""
import io, os, re, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
S = os.path.join(B, 'TXT_分卷', '03_業疏')
T = os.path.join(B, 'AI語譯', 'out', '03_業疏')
GUIDE = json.load(io.open(os.path.join(B, 'AI語譯', '_work', 'ys_offsets.json'), encoding='utf-8'))
OUT = os.path.join(B, 'AI語譯', '_work', 'ys_offsets_final.json')
han = lambda s: len(re.findall(r'[\u4e00-\u9fff]', s))


def corr(a, b):
    n = min(len(a), len(b))
    if n < 8:
        return -9
    a, b = a[:n], b[:n]
    ma, mb = sum(a) / n, sum(b) / n
    num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    da = sum((x - ma) ** 2 for x in a) ** .5
    db = sum((y - mb) ** 2 for y in b) ** .5
    return num / (da * db) if da * db else -9


res = {}
report = []
for f in sorted(os.listdir(S)):
    if not f.endswith('.txt'):
        continue
    k = f[:-4]
    sp = [x.strip() for x in io.open(os.path.join(S, f), encoding='utf-8').read().split('\n')[5:] if x.strip()]
    tt = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(os.path.join(T, k + '.txt'), encoding='utf-8').read()) if x.strip()]
    Ls = [han(x) for x in sp]
    Lt = [han(x) for x in tt]
    best = (0, -9)
    for o in range(-8, 61):
        if o >= 0:
            c = corr(Ls, Lt[o:])
        else:
            c = corr(Ls[-o:], Lt)
        if c > best[1]:
            best = (o, c)
    o, c = best
    if c < 0.60:
        o = int(GUIDE.get(k[:3].rstrip('_'), 0))
        c2 = None
    else:
        c2 = round(c, 3)
    res[k] = o
    report.append((k, o, c2))
json.dump(res, io.open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for k, o, c in report:
    flag = '' if c is not None else '  (回退指引)'
    print('%-16s %+4d  相關 %s%s' % (k, o, c if c is not None else '-', flag))
