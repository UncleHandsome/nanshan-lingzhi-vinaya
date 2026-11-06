# -*- coding: utf-8 -*-
import io, os
from docx import Document

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
doc = Document(os.path.join(B, '合編材料', '合編_人工對齊版.docx'))
paras = [x.text for x in doc.paragraphs]
out = io.StringIO()
out.write('paras=%d\n' % len(paras))
keys = ['出俗五眾', '又上三中', '篇聚者', '名殊義一', '報入二八', '就中，先明戒護', '初中，所以犯戒果報']
for k in keys:
    idx = [i for i, t in enumerate(paras) if k in t]
    out.write('%s -> %s\n' % (k, idx[:10]))
# dump region around first 出俗五眾
for k in ['出俗五眾']:
    for i in [i for i, t in enumerate(paras) if k in t][:2]:
        out.write('\n===== around %d =====\n' % i)
        for j in range(max(0, i - 2), min(len(paras), i + 45)):
            out.write('[%d] %s\n' % (j, paras[j][:90].replace('\n', ' ')))
io.open(os.path.join(B, 'AI語譯', '_work', 'align_fix', '_docx13b.txt'), 'w', encoding='utf-8').write(out.getvalue())
print('ok')
