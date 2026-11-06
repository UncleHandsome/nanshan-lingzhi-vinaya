from docx import Document
import re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
d = Document(B + r'\白話\會本_篇6結界方法.docx')
ps = [p.text.strip() for p in d.paragraphs]
# 印出指定記段前後：原文 + 白話
want = ['【記010】', '【記010】（後半）', '【記026】', '【記026】（後半）',
        '【記068】（後半）', '【記076】（後半）', '【記088】（後半）']
for i, t in enumerate(ps):
    for w in want:
        if t.startswith(w):
            print('=====', t[:24])
            print('  段 :', t[:60])
            print('  譯 :', ps[i + 1][:60] if i + 1 < len(ps) else '')
