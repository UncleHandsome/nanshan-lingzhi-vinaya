# -*- coding: utf-8 -*-
import io, re
from docx import Document
B = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
ps = [x.text for x in Document(B + r"\白話\會本_篇14_隨戒釋相.docx").paragraphs]
K2, K3 = 904, 1656
seg = ps[K2:K3]
out = io.open(B + r"\_tmp_jz2\tags.txt", "w", encoding="utf-8")
i = 0
n = 0
while i < len(seg):
    t = seg[i]
    m = re.match(r'^【(鈔|記)(\d+)】', t)
    if m:
        n += 1
        body = t[m.end():]
        out.write("%s%03d\t%04d\t%s\n" % (m.group(1), int(m.group(2)), K2+i, body[:60]))
        i += 2
    else:
        i += 1
out.close()
print("pairs", n)
