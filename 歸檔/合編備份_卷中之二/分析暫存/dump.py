# -*- coding: utf-8 -*-
import io
from docx import Document
p = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\白話\行事鈔資持記句級合編_卷中之二.docx"
d = Document(p)
ps = [x.text for x in d.paragraphs]
out = io.open(r"C:\Users\lionc\OneDrive\桌面\XW\三大部\_tmp_jz2\dump_卷中之二.txt", "w", encoding="utf-8")
out.write("total paras %d\n" % len(ps))
for i, t in enumerate(ps):
    out.write("%04d\t%r\n" % (i, t))
out.close()
print("ok")
