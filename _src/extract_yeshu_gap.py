
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
# 建立 han index -> raw index
idx = [i for i, ch in enumerate(raw_src) if '\u4e00' <= ch <= '\u9fff' or ch == '〇']
out = ['《四分律刪補隨機羯磨疏》句讀檔缺漏段落（依底本 CBETA X41n0728 補）',
       '共 %d 段，約 %d 字。請只加標點，不改字。' % (len(big), sum(r[1]-r[0]+k for r in big)), '']
for n,(a,b) in enumerate(sorted(big, key=lambda r: r[0]), 1):
    s = idx[a]; e = idx[min(len(idx)-1, b+k-1)]
    body = raw_src[s:e+1]
    out.append('【缺段%d】' % n)
    out.append('（前文：%s）' % src[max(0,a-16):a])
    out.append(body)
    out.append('（後文：%s）' % src[b+k:b+k+16])
    out.append('')
io.open(os.path.join(D,'TXT_句讀','_缺段','03_業疏_缺段.txt'),'w',encoding='utf-8').write('\n'.join(out))
io.open(os.path.join(D,'AI語譯','_work','yeshu_ju_gaps.txt'),'w',encoding='utf-8').write('\n'.join(
    ['coverage %.2f%%' % (100.0*(1-len(miss)*1.0/(len(src)//k)))] +
    ['%d-%d (%d chars)' % (a, b+k, b-a+k) for a,b in sorted(big, key=lambda r: r[0])]))
print('gaps', len(big), 'total chars', sum(r[1]-r[0]+k for r in big))
