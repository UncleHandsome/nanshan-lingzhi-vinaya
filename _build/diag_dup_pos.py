import io, os
from docx import Document

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
d = Document(os.path.join(B, '白話', '行事鈔資持記句級合編_卷上之一.docx'))
ts = [p.text.strip() for p in d.paragraphs]
idx = [i for i, t in enumerate(ts) if '古科列名在十門之首' in t]
print('出現位置', idx)
for i in idx:
    ctx = [x[:36] for x in ts[max(0, i - 4):i + 3]]
    print('---', i)
    for c in ctx:
        print('   ', c)
