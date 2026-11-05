
# -*- coding: utf-8 -*-
from docx import Document
import os
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\白話'
for name in ['業疏_卷一_白話對照本.docx','業疏_卷二_白話對照本.docx']:
    p = os.path.join(D, name)
    d = Document(p)
    txt = '\n'.join(x.text for x in d.paragraphs)
    print(name, 'paras', len(d.paragraphs), '序?', '新刻入註排科' in txt, '大雄' in txt, '卷首' in txt)
