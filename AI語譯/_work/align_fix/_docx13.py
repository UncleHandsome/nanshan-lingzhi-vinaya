# -*- coding: utf-8 -*-
import io, os
from docx import Document

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = os.path.join(B, '合編材料', '合編_人工對齊版.docx')
doc = Document(p)
paras = [x.text for x in doc.paragraphs]
out = io.StringIO()
out.write('paras=%d\n' % len(paras))
# find 篇聚名報 section
hits = [i for i, t in enumerate(paras) if '篇聚' in t]
out.write('hits=%s\n' % hits[:40])
for i in hits[:5]:
    out.write('\n--- around %d ---\n' % i)
    for j in range(max(0, i - 3), min(len(paras), i + 40)):
        t = paras[j].replace('\n', ' ')
        out.write('[%d] %s\n' % (j, t[:100]))
io.open(os.path.join(B, 'AI語譯', '_work', 'align_fix', '_docx13.txt'), 'w', encoding='utf-8').write(out.getvalue())
print('ok')
