
# -*- coding: utf-8 -*-
from docx import Document
import io
p = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\白話\行事鈔資持記合編_上卷.docx'
d = Document(p)
n = len(d.paragraphs); sh = 0
samples = []
for para in d.paragraphs[:60]:
    has = para._p.find('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}shd') is not None
    if has: sh += 1
    if len(samples) < 6: samples.append(('SH' if has else '  ') + ' ' + para.text[:40])
print('paras', n, 'shaded in first 60', sh)
print('\n'.join(samples))
