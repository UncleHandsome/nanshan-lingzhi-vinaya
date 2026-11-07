# -*- coding: utf-8 -*-
"""以 2-gram 重疊自動求 篇13 各 chunk 的白話位移量並修正"""
import os, io, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
han = lambda s: ''.join(re.findall(r'[\u4e00-\u9fff]', s))

def grams(s, n=2):
    h = han(s)
    return {h[i:i + n] for i in range(len(h) - n + 1)}

def score(sp, tt):
    tot = 0
    for a, b in zip(sp, tt):
        tot += len(grams(a) & grams(b))
    return tot

for k in ['05a_卷中之一', '05b_卷中之一', '05c_卷中之一']:
    fp = os.path.join(B, 'TXT_分卷', '01_行事鈔', k + '.txt')
    tp = os.path.join(B, 'AI語譯', 'out', '01_行事鈔', k + '.txt')
    sp = [x.strip() for x in io.open(fp, encoding='utf-8').read().split('\n')[5:] if x.strip()]
    tt = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(tp, encoding='utf-8').read()) if x.strip()]
    best, bestk = -1, 0
    for shift in range(-4, 5):
        pairs = [(sp[i], tt[i + shift]) for i in range(len(sp)) if 0 <= i + shift < len(tt)]
        s2 = score([p[0] for p in pairs], [p[1] for p in pairs])
        if s2 > best:
            best, bestk = s2, shift
    print(k, '最佳位移', bestk, '分數', best)
    if bestk != 0:
        new = [tt[i + bestk] if 0 <= i + bestk < len(tt) else '' for i in range(len(sp))]
        io.open(tp, 'w', encoding='utf-8').write('\n\n'.join(new) + '\n')
        print('  已套用位移', bestk)
