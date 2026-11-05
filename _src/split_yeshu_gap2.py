
# -*- coding: utf-8 -*-
import io, os
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
VAR = {'牀':'床','説':'說','衆':'眾','爲':'為','敎':'教','卽':'即','旣':'既','竝':'並'}
def han(s): return ''.join(VAR.get(ch, ch) for ch in s if '\u4e00' <= ch <= '\u9fff' or ch == '〇')
raw_src = io.open(os.path.join(D,'TXT','03_四分律刪補隨機羯磨疏.txt'), encoding='utf-8').read()
src = han(raw_src)
ju = han(io.open(os.path.join(D,'03_四分律刪補隨機羯磨疏_句讀.txt'), encoding='utf-8').read())
k = 12
jush = set(ju[i:i+k] for i in range(len(ju)-k))
miss = [i for i in range(0, len(src)-k, k) if src[i:i+k] not in jush]
runs = []; cur = None
for i in miss:
    if cur and i <= cur[1]+k: cur[1] = i
    else:
        if cur: runs.append(cur)
        cur = [i, i]
if cur: runs.append(cur)
big = [r for r in runs if r[1]-r[0] >= 24]
big_sorted = sorted(big, key=lambda r: r[1]-r[0], reverse=True)
top2 = sorted(big_sorted[:2], key=lambda r: r[0])
rest = sorted(big_sorted[2:], key=lambda r: r[0])
idx = [i for i, ch in enumerate(raw_src) if '\u4e00' <= ch <= '\u9fff' or ch == '〇']
def grab(a, b):
    s = idx[a]; e = idx[min(len(idx)-1, b+k-1)]
    return raw_src[s:e+1]
outdir = os.path.join(D,'TXT_句讀','_缺段')
groups = [top2[0:1], top2[1:2], rest]
for gi, grp in enumerate(groups, 1):
    total = sum(r[1]-r[0]+k for r in grp)
    lines = ['《四分律刪補隨機羯磨疏》句讀補段（第 %d 份）' % gi,
             '共 %d 段、約 %d 字。請只加標點，一字不改、不分段、不加標題。' % (len(grp), total), '']
    for n, (a, b) in enumerate(grp, 1):
        lines.append('【段%d】' % n)
        lines.append('（前文：%s）' % src[max(0,a-16):a])
        lines.append(grab(a, b))
        lines.append('（後文：%s）' % src[b+k:b+k+16])
        lines.append('')
    io.open(os.path.join(outdir, '03_業疏_缺段%d.txt' % gi), 'w', encoding='utf-8').write('\n'.join(lines))
    print('part', gi, 'segments', len(grp), 'chars', total)
