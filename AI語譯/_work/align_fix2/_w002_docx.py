# -*- coding: utf-8 -*-
import io, os, sys
from docx import Document

p = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\合編材料\合編_人工對齊版.docx'
d = Document(p)
ps = d.paragraphs
print('paras', len(ps))
# find paragraph containing 諸雜
target = None
for i, par in enumerate(ps):
    if '諸雜' in par.text and ('27' in par.text or '篇' in par.text):
        print(i, repr(par.text[:80]), par.style.name)
print('--- first 20 ---')
for i, par in enumerate(ps[:20]):
    print(i, par.style.name, repr(par.text[:60]))
