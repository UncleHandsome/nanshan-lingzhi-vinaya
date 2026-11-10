# -*- coding: utf-8 -*-
import io, re
from docx import Document
B = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
d = Document(B + r"\白話\行事鈔資持記句級合編_卷中之二.docx")
ps = [x.text for x in d.paragraphs if x.text.strip()][3:]
pairs = [(ps[2*k], ps[2*k+1]) for k in range(len(ps)//2)]
out = io.open(B + r"\_tmp_jz2\after.txt", "w", encoding="utf-8")
for k,(tag,tr) in enumerate(pairs):
    out.write('%3d\t%s\n' % (k+1, tag[:52]))
out.close()
print('pairs', len(pairs))
for k in list(range(0,4)) + list(range(38,48)) + list(range(108,120)):
    print(k+1, pairs[k][0][:60])
