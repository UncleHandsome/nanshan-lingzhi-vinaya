# -*- coding: utf-8 -*-
import os, sys
sys.stdout.reconfigure(encoding='utf-8')
ROOT = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
OUT = os.path.join(ROOT, 'AI語譯', 'out')
def paras(book, chunk):
    t = open(os.path.join(OUT, book, chunk + '.txt'), 'rb').read().decode('utf-8-sig')
    return [s for s in (x.rstrip('\r') for x in t.split('\n')) if s.strip()]
p = paras('01_行事鈔', '01b_卷上之一')
print('total', len(p))
for i in range(54, 72):
    print(i + 1, '|', p[i][:80])
