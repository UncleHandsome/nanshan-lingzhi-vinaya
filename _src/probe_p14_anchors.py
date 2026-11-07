import os, re
from docx import Document

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
OLD = r'C:\Users\lionc\OneDrive\桌面\XW\_舊資料_三大部_20261107\合編_舊docx'

def first_orig(vol):
    fp = os.path.join(OLD, '行事鈔資持記句級合編_%s.docx' % vol)
    for p in Document(fp).paragraphs:
        t = p.text.strip()
        if t.startswith('【鈔】') or t.startswith('【記】'):
            return t[3:].strip()[:40]
    return ''

a = first_orig('卷中之二')
b = first_orig('卷中之三')
print('anchor2:', a)
print('anchor3:', b)

p14 = [p.text.strip() for p in Document(os.path.join(B, '白話', '會本_篇14_隨戒釋相.docx')).paragraphs]

def find_idx(anchor):
    if not anchor:
        return None
    key = anchor[:24]
    for i, t in enumerate(p14):
        for pre in ('【記', '【鈔'):
            if t.startswith(pre):
                rest = t[t.find('】') + 1:]
                if rest[:24] == key:
                    return i
    return None

print('k2:', find_idx(a), 'k3:', find_idx(b), 'total:', len(p14))
