from docx import Document

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
d = Document(B + r'\白話\會本_篇6結界方法.docx')
ps = [p.text.strip() for p in d.paragraphs]
for i, t in enumerate(ps):
    if '（後半）' in t[:12]:
        print(t[:18], '||', ps[i + 1][:34] if i + 1 < len(ps) else '')
