import os, re
from docx import Document

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p14 = [p.text.strip() for p in Document(os.path.join(B, '白話', '會本_篇14_隨戒釋相.docx')).paragraphs]
def first_src(vol):
    fp = os.path.join(B, '白話', '行事鈔資持記句級合編_%s.docx' % vol)
    for p in Document(fp).paragraphs:
        t = p.text.strip()
        if t.startswith('【鈔】') or t.startswith('【記】'):
            return t[3:][:40]
    return ''
a = first_src('卷中之二'); b = first_src('卷中之三')
k2 = next((i for i, t in enumerate(p14) if a and t[2:][:40] == a), None)
k3 = next((i for i, t in enumerate(p14) if b and t[2:][:40] == b), None)
print('k2', k2, 'k3', k3, 'len', len(p14))
