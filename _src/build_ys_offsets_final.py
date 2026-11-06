# -*- coding: utf-8 -*-
"""結合 ye_new.txt 指定位移與資料實測，產生最終位移表"""
import io, os, re, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
S = os.path.join(B, 'TXT_分卷', '03_業疏')
T = os.path.join(B, 'AI語譯', 'out', '03_業疏')
guide = json.load(io.open(os.path.join(B, 'AI語譯', '_work', 'ys_offsets.json'), encoding='utf-8'))
han = lambda s: ''.join(re.findall(r'[\u4e00-\u9fff]', s))


def g2(s):
    h = han(s)
    return set(h[i:i + 2] for i in range(len(h) - 1))


out = {}
for f in sorted(os.listdir(S)):
    if not f.endswith('.txt'):
        continue
    key = f[:-4]
    short = key[:3].rstrip('_')
    sp = [x for x in io.open(os.path.join(S, f), encoding='utf-8').read().split('\n')[5:] if x.strip()]
    tt = [x for x in re.split(r'\r?\n\r?\n', io.open(os.path.join(T, key + '.txt'), encoding='utf-8').read()) if x.strip()]
    g = int(guide.get(short, 0))
    best = (g, -1.0)
    for off in range(0, min(80, max(1, len(tt)))):
        tot = n = 0
        for i in range(min(len(sp), 25)):
            j = i + off
            if j >= len(tt):
                break
            a, b = g2(sp[i]), g2(tt[j])
            if not a or not b:
                continue
            tot += len(a & b) / float(len(a | b))
            n += 1
        if n and tot / n > best[1]:
            best = (off, tot / n)
    off, score = best
    if score < 0.03:
        off = g
    out[key] = off
json.dump(out, io.open(os.path.join(B, 'AI語譯', '_work', 'ys_offsets_final.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('分塊', len(out))
for k in sorted(out)[:12]:
    print('  %-16s %+d (guide %s)' % (k, out[k], guide.get(k[:3].rstrip('_'), '-')))
