import io, os, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
S = os.path.join(B, 'TXT_分卷', '03_業疏')
probes = ['受三歸', '三歸法', '安居法', '安居', '懺六聚', '懺悔', '受戒篇', '受法篇', '自恣法']
for f in sorted(os.listdir(S), key=lambda x: (0 if x.startswith('00_') else 1, x)):
    if not f.endswith('.txt'):
        continue
    sp = [x.strip() for x in io.open(os.path.join(S, f), encoding='utf-8').read().split('\n')[5:] if x.strip()]
    for i, p in enumerate(sp, 1):
        if len(p) > 40:
            continue
        for n in probes:
            if n in p:
                print('%-14s #%-3d %-8s | %s' % (f[:-4], i, n, p[:44]))
