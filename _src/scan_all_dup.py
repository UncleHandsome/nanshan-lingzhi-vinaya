import glob, os, collections
from docx import Document

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
pats = ['戒疏_*.docx', '尼鈔_*.docx', '尼義鈔_*.docx', '業疏_*.docx']
for pat in pats:
    for f in sorted(glob.glob(os.path.join(B, '白話', pat))):
        d = Document(f)
        ps = [p.text.strip() for p in d.paragraphs if len(p.text.strip()) > 30]
        c = collections.Counter(ps)
        dup = {k: v for k, v in c.items() if v > 1}
        print('%-42s 段落%5d 重複種類%3d 多印%4d' % (os.path.basename(f), len(ps), len(dup),
                                                  sum(v - 1 for v in dup.values())))
