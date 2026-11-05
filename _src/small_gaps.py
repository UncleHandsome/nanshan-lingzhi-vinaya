
# -*- coding: utf-8 -*-
import io, os
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
def han(s): return ''.join(ch for ch in s if '\u4e00' <= ch <= '\u9fff' or ch == '〇')
src = han(io.open(os.path.join(D,'TXT','03_四分律刪補隨機羯磨疏.txt'), encoding='utf-8').read())
out=[]
for a in [10848,15084,39444,39588,292920]:
    out.append('--- %d ---' % a)
    out.append(src[max(0,a-20):a] + '【' + src[a:a+36] + '】' + src[a+36:a+56])
io.open(os.path.join(D,'AI語譯','_work','yeshu_small_gaps.txt'),'w',encoding='utf-8').write('\n'.join(out))
print('ok')
