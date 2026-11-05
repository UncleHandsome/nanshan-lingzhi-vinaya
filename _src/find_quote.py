
# -*- coding: utf-8 -*-
import os, io, json, re, sys
BASE = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
OUT = os.path.join(BASE, 'AI語譯', 'out', '01_行事鈔')
SRC = os.path.join(BASE, 'TXT_分卷', '01_行事鈔')

def load():
    items = []
    for f in sorted(os.listdir(OUT)):
        if not f.endswith('.txt'): continue
        key = f[:-4]
        paras = [p.strip() for p in re.split(r'\n\s*\n', io.open(os.path.join(OUT, f), encoding='utf-8').read()) if p.strip()]
        srcp = [x.strip() for x in io.open(os.path.join(SRC, f), encoding='utf-8').read().split('\n')[5:] if x.strip()]
        items.append((key, srcp, paras))
    return items

def locate(q, items):
    q = q.strip()
    hits = []
    for key, srcp, paras in items:
        for i, p in enumerate(paras):
            if q and q in p:
                hits.append((key, i, 'TR', p))
        for i, p in enumerate(srcp):
            if q and q in p:
                hits.append((key, i, 'SRC', p))
    return hits

if __name__ == '__main__':
    qs = json.load(io.open(sys.argv[1], encoding='utf-8'))
    items = load()
    for it in qs:
        q = it.get('quote', '')
        hits = locate(q, items)
        print('---', it.get('page'), it.get('kind'), q)
        if not hits:
            print('   NOT FOUND')
        for h in hits[:3]:
            print('   %s [%d] %s: %s' % (h[0], h[1], h[2], h[3][:80]))
