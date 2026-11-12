import sys, os
sys.path.insert(0, r'C:\Users\lionc\OneDrive\桌面\XW\三大部')
from _r3w_lib import *

checks = [
 ('02_戒疏','06a_卷二上之二',[28,29,31,35,36,38,43,67,68,72,74,75,97,98,101,102,103,104,106,108,131]),
 ('02_戒疏','06b_卷二上之二',[2,3,5,6,7,8,10,11,12,14,19,20,29,32,33,35,38,39]),
 ('02_戒疏','09a_卷二下之二',[120,121,124,125,126,127,133]),
]
out = []
for book, chunk, idxs in checks:
    text = read_text(book, chunk)
    for i in idxs:
        out.append('='*6 + f' {book} {chunk} #{i}')
        out.append(para_of(text, i))
        out.append('')
open('_r3w_check2.txt','w',encoding='utf-8').write('\n'.join(out))
print('written', len(out))
