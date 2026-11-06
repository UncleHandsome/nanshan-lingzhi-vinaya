# -*- coding: utf-8 -*-
"""診斷：業疏每塊 sp/tt 在固定位移下的相關性"""
import io, os, re
import numpy as np

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
S = os.path.join(B, 'TXT_分卷', '03_業疏')
T = os.path.join(B, 'AI語譯', 'out', '03_業疏')
han = lambda s: len(re.findall(r'[\u4e00-\u9fff]', s))

rows = []
for f in sorted(os.listdir(S), key=lambda x: (0 if x.startswith('00_') else 1, x)):
    if not f.endswith('.txt'):
        continue
    k = f[:-4]
    sp = [x.strip() for x in io.open(os.path.join(S, f), encoding='utf-8').read().split('\n')[5:] if x.strip()]
    tp = os.path.join(T, k + '.txt')
    if not os.path.exists(tp):
        continue
    tt = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(tp, encoding='utf-8').read()) if x.strip()]
    if not sp or not tt:
        continue
    a = np.array([han(x) for x in sp], float)
    b = np.array([han(x) for x in tt], float)
    best, bs = None, -9
    for off in range(-12, 13):
        if off >= 0:
            x, y = a[:len(a) - off] if off else a, b[off:]
        else:
            x, y = a[-off:], b[:len(b) + off]
        n = min(len(x), len(y))
        if n < 8:
            continue
        c = np.corrcoef(x[:n], y[:n])[0, 1]
        if c > bs:
            bs, best = c, off
    rows.append((k, len(sp), len(tt), best, round(bs, 2)))

print('%-16s sp   tt  最佳位移 相關' % '分塊')
low = 0
for r in rows:
    flag = '' if r[4] >= 0.8 else '  <<'
    if r[4] < 0.8:
        low += 1
    print('%-16s %4s %4s %5s %6s%s' % (r[0], r[1], r[2], r[3], r[4], flag))
print('低相關(<0.8) 分塊', low, '/', len(rows))
