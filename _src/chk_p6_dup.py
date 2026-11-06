from docx import Document
import re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
d = Document(B + r'\白話\會本_篇6結界方法.docx')
ps = [p.text.strip() for p in d.paragraphs]
# 重複檢查
from collections import Counter
c = Counter(t for t in ps if t.startswith('【記026】'))
print('記026 出現次數', c)
for i, t in enumerate(ps):
    if t.startswith('【記026】'):
        print('---', i)
        print('  古文:', t[:50])
        print('  白話:', ps[i + 1][:50])
# 檢查 088 四片
for i, t in enumerate(ps):
    if t.startswith('【記088】'):
        print('088 片:', t[:34], '||', ps[i + 1][:30])
