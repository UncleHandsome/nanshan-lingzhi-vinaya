from docx import Document

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\白話'
d = Document(B + r'\會本_篇18_四藥受淨.docx')
ps = [p.text.strip() for p in d.paragraphs]
for i, t in enumerate(ps):
    if t.startswith('【記098】'):
        print(t[:12], '|', ps[i + 1][:42])
d2 = Document(B + r'\會本_篇14_隨戒釋相.docx')
q = [p.text.strip() for p in d2.paragraphs]
for i, t in enumerate(q):
    if t.startswith('【記043】') or t.startswith('【記044】'):
        print(t[:10], '|', q[i + 1][:30], '...', q[i + 1][-22:])
