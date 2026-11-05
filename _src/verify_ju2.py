
# -*- coding: utf-8 -*-
import io
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
pairs = [('TXT/04_四分律比丘尼鈔.txt','04_四分律比丘尼鈔_句讀.txt','尼鈔'),
         ('TXT/05_四分律拾毗尼義鈔.txt','05_四分律拾毗尼義鈔_句讀.txt','義鈔')]
def han(s):
    return ''.join(ch for ch in s if '\u4e00' <= ch <= '\u9fff' or ch == '〇')
for srcp, jup, name in pairs:
    src = han(io.open(B+'/'+srcp, encoding='utf-8').read())
    ju  = han(io.open(B+'/'+jup, encoding='utf-8').read())
    k = 12
    jush = set(ju[i:i+k] for i in range(len(ju)-k))
    miss = []
    total = 0
    for i in range(0, len(src)-k, k):
        seg = src[i:i+k]
        total += 1
        if seg not in jush: miss.append((i, seg))
    print(name, 'src', len(src), 'ju', len(ju), 'coverage %.1f%%' % (100.0*(total-len(miss))/total), 'missing', len(miss))
    # 連續缺失區塊
    runs = []
    cur = None
    for i, seg in miss:
        if cur and i <= cur[1] + k:
            cur[1] = i
        else:
            if cur: runs.append(tuple(cur))
            cur = [i, i]
    if cur: runs.append(tuple(cur))
    print('   gap blocks', len(runs), 'largest:', sorted(runs, key=lambda r: r[1]-r[0], reverse=True)[:3])
    for a, b in sorted(runs, key=lambda r: r[1]-r[0], reverse=True)[:2]:
        print('     src[%d:%d] = %s' % (a, b+k, src[a:a+40]))
