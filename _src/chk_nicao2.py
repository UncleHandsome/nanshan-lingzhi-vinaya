
# -*- coding: utf-8 -*-
import io
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
def han(s): return ''.join(ch for ch in s if '\u4e00' <= ch <= '\u9fff' or ch == '〇')
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
lines = ['coverage %.2f%%' % (100.0*(1-len(miss)*1.0/max(1,(len(src)//k))))]
for a,b in runs:
    if b-a >= 6:
        lines.append('gap %d-%d (%d chars) before=%s after=%s' % (a, b+k, b-a+k, src[max(0,a-10):a], src[a:a+16]))
io.open(D+'\\AI語譯\\_work\\nicao_gaps.txt','w',encoding='utf-8').write('\n'.join(lines))
print(lines[0], 'gaps', len(runs))
