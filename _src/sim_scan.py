
# -*- coding: utf-8 -*-
import os, io, re
from difflib import SequenceMatcher
BASE = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
S = os.path.join(BASE,'TXT_分卷','01_行事鈔'); T = os.path.join(BASE,'AI語譯','out','01_行事鈔')
pat = re.compile(r'^\d+\s+.*篇\([上中下][一二三四]\)$')
jp = re.compile(r'^[\u4e00-\u9fff]{2,10}篇第[\u4e00-\u9fff]+$')
rows = []
for f in sorted(os.listdir(S)):
    if not f.endswith('.txt') or f.startswith('00_'): continue
    key = f[:-4]
    sp = [x.strip() for x in io.open(os.path.join(S,f),encoding='utf-8').read().split('\n')[5:] if x.strip() and not pat.match(x.strip())]
    tp = [x.strip() for x in re.split(r'\n\s*\n', io.open(os.path.join(T,key+'.txt'),encoding='utf-8').read()) if x.strip() and not pat.match(x.strip())]
    i = 0
    while i < len(sp) and not jp.match(sp[i]): i += 1
    j = i
    while j < len(sp) and jp.match(sp[j]): j += 1
    if j - i >= 3 and j < len(sp):
        del sp[i:j]
        if len(tp) > j: del tp[i:j]
    for k in range(min(len(sp), len(tp))):
        a, b = sp[k], tp[k]
        if len(a) < 40: continue
        r = SequenceMatcher(None, a, b).ratio()
        if r > 0.55:
            rows.append((r, key, k+1, a[:40], b[:40]))
rows.sort(reverse=True)
print('suspicious', len(rows))
for r,k,i,a,b in rows[:40]:
    print('%.2f %s p%d | %s || %s' % (r, k, i, a, b))
