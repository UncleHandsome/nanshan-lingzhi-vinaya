# -*- coding: utf-8 -*-
import io, os, re
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

PATS = re.compile(r'^([\u4e00-\u9fff]{2,8})篇第([一二三四五六七八九十]+)$')
PATS2 = re.compile(r'^\d+\s*[\u4e00-\u9fff]{2,10}篇\(上[一二三四五六七八九十]?\)$')
secs, cur = [], None
for k, sp in load('01_行事鈔'):
    for o in sp:
        if PATS2.match(o.strip()):
            continue
        m = PATS.match(o)
        if m:
            if any(x['no'] == m.group(2) for x in secs):
                cur = next(x for x in secs if x['no'] == m.group(2))
            else:
                cur = dict(name=m.group(1), no=m.group(2), items=[]); secs.append(cur)
            continue
        if cur is not None:
            cur['items'].append(o)

C = secs[13]['items']
cl = [len(han(x)) for x in C]
lines = ['C n=%d total=%d mean=%.1f' % (len(C), sum(cl), sum(cl) / len(cl))]
for a, b in [(0, 100), (100, 200), (200, 320)]:
    seg = cl[a:b]
    lines.append('C[%d:%d] n=%d chars=%d mean=%.1f' % (a, b, len(seg), sum(seg), sum(seg) / len(seg)))
# cumulative fraction at some indexes
acc = 0.0
cum = []
for L in cl:
    acc += L
    cum.append(acc / sum(cl))
for j in (10, 50, 102, 114, 145, 155, 200, 250, 319):
    lines.append('cum_c[%d]=%.4f  count-frac=%.4f  head=%s' % (j, cum[j], j / 320.0, C[j][:25]))
io.open(os.path.join(AD, '_diag2.txt'), 'w', encoding='utf-8').write('\n'.join(lines))
print('ok')
