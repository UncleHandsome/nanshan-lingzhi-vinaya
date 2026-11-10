# -*- coding: utf-8 -*-
import io, re
from docx import Document
B = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
hb = [p.text for p in Document(B + r"\白話\行事鈔資持記句級合編_卷中之二.docx").paragraphs]
src = [x.text for x in Document(B + r"\白話\會本_篇14_隨戒釋相.docx").paragraphs][904:1656]
print('hb paras', len(hb), 'src', len(src))
print('hb head', [t[:20] for t in hb[:4]])
# pairs
hp = [t for t in hb if t.strip()][3:]
print('hb pair paras', len(hp))
# src pair paras
sp = []
i = 0
while i < len(src):
    m = re.match(r'^【(鈔|記)(\d+)】(（[^）]*）)?', src[i])
    if m:
        body = src[i][m.end():]
        sp.append('【%s】%s' % (m.group(1), body))
        sp.append(src[i+1] if i+1 < len(src) else '')
        i += 2
    else:
        i += 1
print('src pair paras', len(sp))
diff = 0
for k in range(min(len(hp), len(sp))):
    if hp[k] != sp[k]:
        diff += 1
        if diff <= 5:
            print('DIFF', k, repr(hp[k][:40]), '|', repr(sp[k][:40]))
print('diffs', diff)
