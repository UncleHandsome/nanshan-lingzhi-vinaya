# -*- coding: utf-8 -*-
import io, os, sys, zipfile, re
sys.stdout.reconfigure(encoding='utf-8')
p = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\合編材料\合編_人工對齊版.docx'
print(os.path.getsize(p))
z = zipfile.ZipFile(p)
print([n for n in z.namelist()][:20])
import docx
d = docx.Document(p)
print('paras', len(d.paragraphs))
for i, par in enumerate(d.paragraphs[:40]):
    t = par.text.strip()
    print(i, par.style.name, '|', t[:80])
