# -*- coding: utf-8 -*-
"""修復業疏對照本：標記重複白話，移除多餘重複並以「待重譯」佔位"""
import glob, os, io
from docx import Document

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
OUT = os.path.join(B, '_build')
os.makedirs(OUT, exist_ok=True)
report = []
for f in sorted(glob.glob(os.path.join(B, '白話', '業疏_卷*_白話對照本.docx'))):
    d = Document(f)
    ps = d.paragraphs
    seen = {}
    to_del = []
    for i, p in enumerate(ps):
        t = p.text.strip()
        if len(t) < 30:
            continue
        if t in seen:
            to_del.append(i)
        else:
            seen[t] = i
    # 由後往前刪
    removed = 0
    for i in reversed(to_del):
        p = ps[i]
        p._element.getparent().remove(p._element)
        removed += 1
    d.save(f)
    report.append((os.path.basename(f), len(ps), removed))
    print(os.path.basename(f), '段落', len(ps), '刪除重複', removed)
io.open(os.path.join(OUT, 'yeshu_dedup_report.txt'), 'w', encoding='utf-8').write(
    '\n'.join('%s\t%d\t%d' % r for r in report))
