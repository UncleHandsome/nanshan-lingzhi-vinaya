
from docx import Document
p = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\白話\行事鈔_白話對照本_上卷.docx'
d = Document(p)
for i, para in enumerate(d.paragraphs[:28]):
    t = para.text.strip().replace('\n', ' ')
    fill = 'SHADE' if para._p.find('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}shd') is not None else '     '
    print(i, fill, t[:50])
