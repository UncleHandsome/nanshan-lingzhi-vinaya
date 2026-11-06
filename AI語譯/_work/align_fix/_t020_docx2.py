# -*- coding: utf-8 -*-
import sys, docx
sys.stdout.reconfigure(encoding='utf-8')
p = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\合編材料\合編_人工對齊版.docx'
d = docx.Document(p)
paras = [x.text.strip() for x in d.paragraphs]
# find section marker
idx = [i for i,t in enumerate(paras) if '四藥受淨' in t]
print('四藥受淨 hits', idx[:10])
for i in idx[:3]:
    print('---', i)
    for j in range(max(0,i-2), min(len(paras), i+8)):
        print(j, '|', paras[j][:100])
