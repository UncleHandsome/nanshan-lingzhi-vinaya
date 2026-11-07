# -*- coding: utf-8 -*-
"""盤點業疏對照本的重複白話，列出對應原文範圍"""
import glob, os, io, re
from docx import Document

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
lines = ['# 業疏對照本重複白話盤點', '']
for f in sorted(glob.glob(os.path.join(B, '白話', '業疏_卷*_白話對照本.docx'))):
    d = Document(f)
    ps = [p.text.strip() for p in d.paragraphs]
    seen = {}
    dup = {}
    last_src = ''
    for i, t in enumerate(ps):
        if t.startswith('【疏】') or t.startswith('【記】'):
            last_src = t
            continue
        if len(t) < 30:
            continue
        if t in seen:
            dup.setdefault(t, []).append(last_src)
        else:
            seen[t] = i
    vol = re.search(r'卷(.)', os.path.basename(f)).group(1)
    lines.append('## 卷%s：重複種類 %d，重複段落 %d' % (vol, len(dup), sum(len(v) - 1 for v in dup.values())))
    lines.append('')
    for t, srcs in list(dup.items())[:8]:
        lines.append('- 重複 %d 次｜白話：%s…' % (len(srcs) + 1, t[:40]))
        lines.append('  - 首見原文：%s' % srcs[0][:60])
        lines.append('  - 最後原文：%s' % srcs[-1][:60])
    lines.append('')
io.open(os.path.join(B, '業疏重複白話報告.md'), 'w', encoding='utf-8').write('\n'.join(lines))
print('\n'.join(lines[:20]))
