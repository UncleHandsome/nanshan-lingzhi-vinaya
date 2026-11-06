# -*- coding: utf-8 -*-
"""業疏：以「首句錨點 + 位移」重建 sp→tt 對應（位移模型）"""
import io, os, re, json
import numpy as np

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
S = os.path.join(B, 'TXT_分卷', '03_業疏')
T = os.path.join(B, 'AI語譯', 'out', '03_業疏')
han = lambda s: ''.join(re.findall(r'[\u4e00-\u9fff]', s))
hcnt = lambda s: len(re.findall(r'[\u4e00-\u9fff]', s))

out = {}
rows = []
for f in sorted(os.listdir(S), key=lambda x: (0 if x.startswith('00_') else 1, x)):
    if not f.endswith('.txt'):
        continue
    k = f[:-4]
    sp = [x.strip() for x in io.open(os.path.join(S, f), encoding='utf-8').read().split('\n')[5:] if x.strip()]
    tp = os.path.join(T, k + '.txt')
    if not os.path.exists(tp) or not sp:
        continue
    tt = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(tp, encoding='utf-8').read()) if x.strip()]
    if not tt:
        continue
    # 1) 首句錨點
    off = None
    for L in (16, 12, 8):
        probe = han(sp[0])[:L]
        if len(probe) < L:
            continue
        for j, t in enumerate(tt[:60]):
            if probe and probe in han(t):
                off = j
                break
        if off is not None:
            break
    # 2) 位移相關性（備援）
    corr = None
    if off is None:
        a = np.array([hcnt(x) for x in sp], float)
        b = np.array([hcnt(x) for x in tt], float)
        best = (-9, None)
        for o in range(-80, 81):
            if o >= 0:
                x, y = a, b[o:]
            else:
                x, y = a[-o:], b
            n = min(len(x), len(y))
            if n < 20:
                continue
            c = np.corrcoef(x[:n], y[:n])[0, 1]
            if c > best[0]:
                best = (c, o)
        corr, off = best
    # 驗證
    mp = []
    for i in range(len(sp)):
        j = i + (off or 0)
        mp.append(j if 0 <= j < len(tt) else min(max(j, 0), len(tt) - 1))
    good = sum(1 for i in range(min(len(sp), len(tt))) if 0 <= i + (off or 0) < len(tt))
    rows.append((k, len(sp), len(tt), off, round(corr, 2) if corr else '-'))
    out[k] = mp

print('%-16s sp   tt  位移 相關' % '分塊')
for r in rows:
    print('%-16s %4s %4s %4s %6s' % r)
json.dump(out, io.open(os.path.join(B, 'AI語譯', '_work', 'ys_align_map.json'), 'w', encoding='utf-8'), ensure_ascii=False)
print('寫入 ys_align_map.json（位移模型）', len(out), '塊')
