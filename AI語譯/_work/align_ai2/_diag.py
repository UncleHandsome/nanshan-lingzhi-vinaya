# -*- coding: utf-8 -*-
import io, os, re, json
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
AD = os.path.join(B, 'AI語譯', '_work', 'align_ai2')
han = lambda s: ''.join(re.findall(r'[\u4e00-\u9fff]', s))

def load(src):
    S = os.path.join(B, 'TXT_分卷', src)
    out = []
    for f in sorted(os.listdir(S), key=lambda x: (0 if x.startswith('00_') else 1, x)):
        if f.endswith('.txt'):
            out.append((f[:-4], [x.strip() for x in io.open(os.path.join(S, f), encoding='utf-8').read().split('\n')[5:] if x.strip()]))
    return out

ZP = re.compile(r'釋([\u4e00-\u9fff]{2,6})篇')
zj = []
for k, sp in load('資持記_細分'):
    zj += sp
zs, z = [], None
for o in zj:
    if ZP.search(o):
        z = []
        zs.append(z)
    if z is not None:
        z.append(o)
zi = zs[15] + zs[16] + zs[17]
lines = []
for i, nm in [(15, '持犯'), (16, '懺六聚'), (17, '二衣')]:
    L = [len(han(x)) for x in zs[i]]
    lines.append('%s n=%d chars=%d mean=%.1f' % (nm, len(L), sum(L), sum(L) / len(L)))
Lb = [len(han(x)) for x in zi[300:450]]
lines.append('batch slice z300..449: n=%d chars=%d mean=%.1f' % (len(Lb), sum(Lb), sum(Lb) / len(Lb)))
zall = [len(han(x)) for x in zi]
lines.append('zi total chars=%d mean=%.1f' % (sum(zall), sum(zall) / len(zall)))
pref = [0.0]
for L in zall:
    pref.append(pref[-1] + L / float(sum(zall)))
for zz in (300, 330, 360, 389, 420, 449):
    lines.append('pref[%d]=%.4f -> count-frac=%.4f' % (zz, pref[zz], zz / 662.0))
io.open(os.path.join(AD, '_diag.txt'), 'w', encoding='utf-8').write('\n'.join(lines))
print('\n'.join(lines).encode('utf-8').decode('utf-8'))
