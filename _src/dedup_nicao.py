import glob, os
from docx import Document

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
for f in glob.glob(os.path.join(B, '白話', '尼鈔_卷*_白話對照本.docx')):
    d = Document(f)
    seen, todel = set(), []
    for p in d.paragraphs:
        t = p.text.strip()
        if len(t) < 30:
            continue
        if t in seen:
            todel.append(p)
        else:
            seen.add(t)
    for p in todel:
        p._element.getparent().remove(p._element)
    d.save(f)
    print(os.path.basename(f), '刪除', len(todel))
