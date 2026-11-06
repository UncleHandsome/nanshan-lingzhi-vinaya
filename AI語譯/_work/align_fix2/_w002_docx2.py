# -*- coding: utf-8 -*-
import io, os
from docx import Document

p = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\合編材料\合編_人工對齊版.docx'
d = Document(p)
ps = d.paragraphs
out = []
# find start of 篇27
start = None
for i, par in enumerate(ps):
    if par.text.strip().startswith('【記】27') or ('27 釋諸雜篇' in par.text and i > 10000):
        start = i
        break
out.append('start index %s' % start)
# find end: 篇28 heading
end = None
for i in range(start, min(len(ps), start + 400)):
    if '28 沙彌別行篇' in ps[i].text or ps[i].text.strip().startswith('【記】28') or ps[i].text.strip().startswith('篇28'):
        end = i
        break
out.append('end index %s' % end)
for i in range(max(0, start - 6), min(len(ps), (end or start + 200) + 6)):
    par = ps[i]
    t = par.text.strip()
    if not t:
        continue
    runs = par.runs
    sz = ''
    if runs:
        try:
            sz = str(runs[0].font.size)
        except Exception:
            sz = ''
    out.append('%d | %s | sz=%s | %s' % (i, par.style.name, sz, t[:70]))
io.open(os.path.join(os.path.dirname(__file__), '_w002_docx_dump.txt'), 'w', encoding='utf-8').write('\n'.join(out))
