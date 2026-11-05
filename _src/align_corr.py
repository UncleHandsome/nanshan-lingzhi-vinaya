
# -*- coding: utf-8 -*-
import os, io, re
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
BOOKS = [('01_行事鈔','01_行事鈔'),('03_業疏','03_業疏'),('02_戒疏','02_戒疏'),
         ('04_比丘尼鈔','04_比丘尼鈔'),('資持記','資持記_細分'),('05_拾毗尼義鈔','05_拾毗尼義鈔')]
def rank(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0]*len(xs)
    for pos, i in enumerate(order): r[i] = pos
    return r
def corr(a, b):
    n = len(a)
    if n < 5: return 1.0
    ra, rb = rank(a), rank(b)
    ma, mb = sum(ra)/n, sum(rb)/n
    num = sum((x-ma)*(y-mb) for x, y in zip(ra, rb))
    da = sum((x-ma)**2 for x in ra) ** 0.5
    db = sum((y-mb)**2 for y in rb) ** 0.5
    return num/(da*db) if da*db else 0.0
for tag, src in BOOKS:
    S = os.path.join(B,'TXT_分卷',src); O = os.path.join(B,'AI語譯','out',tag)
    if not os.path.isdir(O): continue
    bad = []
    for f in sorted(os.listdir(S)):
        if not f.endswith('.txt'): continue
        key = f[:-4]; p = os.path.join(O, key+'.txt')
        if not os.path.exists(p): continue
        raw = io.open(os.path.join(S,f),encoding='utf-8').read().split('\n')[5:]
        spP = [x for x in re.split(r'\n\s*\n', '\n'.join(raw)) if x.strip()]
        spL = [x for x in raw if x.strip()]
        sp = spP if len(spP) >= len(spL) else spL
        tp = [x.strip() for x in re.split(r'\n\s*\n', io.open(p,encoding='utf-8').read()) if x.strip()]
        n = min(len(sp), len(tp))
        c = corr([len(x) for x in sp[:n]], [len(x) for x in tp[:n]])
        if c < 0.35: bad.append((key, round(c,2), len(sp), len(tp)))
    print(tag, 'chunks', len([1 for f in os.listdir(S) if f.endswith('.txt')]), 'low-corr', len(bad))
    for x in bad[:6]: print('   ', x)
