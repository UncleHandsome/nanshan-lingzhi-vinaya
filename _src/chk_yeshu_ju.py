
# -*- coding: utf-8 -*-
import io, os, re
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
VAR = {'牀':'床','説':'說','衆':'眾','爲':'為','敎':'教','卽':'即','旣':'既','竝':'並','綫':'線','決':'决'}
def han(s): return ''.join(VAR.get(ch, ch) for ch in s if '\u4e00' <= ch <= '\u9fff' or ch == '〇')
src = han(io.open(os.path.join(D,'TXT','03_四分律刪補隨機羯磨疏.txt'), encoding='utf-8').read())
ju  = han(io.open(os.path.join(D,'03_四分律刪補隨機羯磨疏_句讀.txt'), encoding='utf-8').read())
k = 12
jush = set(ju[i:i+k] for i in range(len(ju)-k))
tot = len(src)//k
miss = [i for i in range(0, len(src)-k, k) if src[i:i+k] not in jush]
runs = []; cur = None
for i in miss:
    if cur and i <= cur[1]+k: cur[1] = i
    else:
        if cur: runs.append(cur)
        cur = [i, i]
if cur: runs.append(cur)
print('src', len(src), 'ju', len(ju), 'coverage %.2f%%' % (100.0*(1-len(miss)*1.0/tot)))
print('runs', len(runs))
for a,b in sorted(runs, key=lambda r: r[1]-r[0], reverse=True)[:8]:
    print('  %d-%d (%d) before=%s after=%s' % (a, b+k, b-a+k, src[max(0,a-12):a], src[a:a+16]))
