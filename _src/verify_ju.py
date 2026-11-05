
# -*- coding: utf-8 -*-
import io, re
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
pairs = [('TXT/04_四分律比丘尼鈔.txt','04_四分律比丘尼鈔_句讀.txt','尼鈔'),
         ('TXT/05_四分律拾毗尼義鈔.txt','05_四分律拾毗尼義鈔_句讀.txt','義鈔')]
def han(s):
    return ''.join(ch for ch in s if '\u4e00' <= ch <= '\u9fff' or ch in '〇')
for srcp, jup, name in pairs:
    src = han(io.open(B+'/'+srcp, encoding='utf-8').read())
    ju  = han(io.open(B+'/'+jup, encoding='utf-8').read())
    # 去抬頭（我們 TXT 前幾行是書名資訊）
    k = 10
    sh = set(src[i:i+k] for i in range(0, len(src)-k, k))
    jush = set(ju[i:i+k] for i in range(0, len(ju)-k, k))
    hit = len(sh & jush)
    print(name, 'src', len(src), 'ju', len(ju), 'ratio %.2f' % (len(ju)/len(src)),
          'coverage %.1f%%' % (100.0*hit/len(sh)))
    # 找出 src 中缺失的段落（連續 miss 的取樣）
    miss = []
    for i in range(0, len(src)-k, k):
        seg = src[i:i+k]
        if seg not in jush:
            miss.append((i, seg))
    print('   missing segments', len(miss), 'first:', miss[:3])
