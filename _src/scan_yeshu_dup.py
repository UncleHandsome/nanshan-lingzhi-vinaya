import glob, os, collections
from docx import Document

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
for f in sorted(glob.glob(os.path.join(B, '白話', '業疏_卷*_白話對照本.docx'))):
    d = Document(f)
    ps = [p.text.strip() for p in d.paragraphs if len(p.text.strip()) > 30]
    c = collections.Counter(ps)
    dup = {k: v for k, v in c.items() if v > 1}
    print(os.path.basename(f), '段落', len(ps), '重複種類', len(dup), '重複總數', sum(v - 1 for v in dup.values()))
    for k, v in list(dup.items())[:3]:
        print('  x%d %s' % (v, k[:50]))
