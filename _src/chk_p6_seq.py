from docx import Document
import re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
d = Document(B + r'\白話\會本_篇6結界方法.docx')
seq = []
for p in d.paragraphs:
    t = p.text.strip()
    m = re.match(r'^【鈔(\d+)】', t)
    if m:
        seq.append('鈔' + m.group(1)); continue
    m = re.match(r'^【記(\d+)(】|】（後半）)', t)
    if m:
        seq.append('記' + m.group(1) + ('後' if '後半' in t[:12] else ''))
print(' '.join(seq))
