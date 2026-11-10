# -*- coding: utf-8 -*-
import sys, io
from docx import Document
p = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\白話\行事鈔資持記句級合編_卷中之二.docx"
d = Document(p)
ps = [x.text for x in d.paragraphs]
print("total paras", len(ps))
for i, t in enumerate(ps[:40]):
    print(i, repr(t[:90]))
