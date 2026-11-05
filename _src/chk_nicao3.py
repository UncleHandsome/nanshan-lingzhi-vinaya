
# -*- coding: utf-8 -*-
import io
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
VAR = {'牀':'床','説':'說','衆':'眾','爲':'為','敎':'教','卽':'即','旣':'既','竝':'並','衹':'只','喫':'吃','麁':'粗','麤':'粗','爾':'尔','佗':'他'}
def han(s):
    return ''.join(VAR.get(ch, ch) for ch in s if '\u4e00' <= ch <= '\u9fff' or ch == '〇')
src = han(io.open(D+'\\TXT\\04_四分律比丘尼鈔.txt', encoding='utf-8').read())
ju = han(io.open(D+'\\04_四分律比丘尼鈔_句讀_v2.txt', encoding='utf-8').read())
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
print('coverage %.2f%%' % (100.0*(1-len(miss)*1.0/max(1,(len(src)//k)))))
print('runs', len(runs), 'big', len(big))
for a,b in big[:8]:
    print('  %d-%d %s | %s' % (a, b+k, src[max(0,a-8):a], src[a:a+18]))
