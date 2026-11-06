import io, os, re
import numpy as np

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
S = os.path.join(B, 'TXT_分卷', '03_業疏')
T = os.path.join(B, 'AI語譯', 'out', '03_業疏')
han = lambda s: len(re.findall(r'[\u4e00-\u9fff]', s))
for k in ['04b_卷一之四', '05a_卷一之五', '10a_卷二之四', '17b_卷三之六']:
    sp = [x.strip() for x in io.open(os.path.join(S, k + '.txt'), encoding='utf-8').read().split('\n')[5:] if x.strip()]
    tt = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(os.path.join(T, k + '.txt'), encoding='utf-8').read()) if x.strip()]
    a = np.array([han(x) for x in sp], float)
    b = np.array([han(x) for x in tt], float)
    best = (-9, None)
    for off in range(-60, 61):
        if off >= 0:
            x, y = a, b[off:]
        else:
            x, y = a[-off:], b
        n = min(len(x), len(y))
        if n < 10:
            continue
        c = np.corrcoef(x[:n], y[:n])[0, 1]
        if c > best[0]:
            best = (c, off)
    print('%-14s 最佳位移 %4d 相關 %.2f' % (k, best[1], best[0]))
