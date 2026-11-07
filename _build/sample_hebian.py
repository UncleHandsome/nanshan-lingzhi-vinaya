import io, os, re
from docx import Document

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
HB = ['卷上之一', '卷上之二', '卷上之三']
for vol in HB:
    d = Document(os.path.join(B, '白話', '行事鈔資持記句級合編_%s.docx' % vol))
    seq = []
    for p in d.paragraphs:
        t = p.text.strip()
        if t.startswith('【鈔】'):
            seq.append(('c', t[3:]))
        elif t.startswith('【記】'):
            seq.append(('j', t[3:]))
        elif t.startswith('第') and '篇' in t:
            seq.append(('h', t))
    print('=====', vol, 'pair items', len(seq))
    shown = 0
    for i, (k, t) in enumerate(seq):
        if k == 'c' and shown < 4:
            print('  鈔:', t[:44])
            for j in range(i + 1, min(i + 4, len(seq))):
                if seq[j][0] == 'j':
                    print('    記:', seq[j][1][:44])
            shown += 1
