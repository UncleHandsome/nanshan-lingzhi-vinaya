# -*- coding: utf-8 -*-
import io, re
from docx import Document
B = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
p = B + r"\白話\會本_篇14_隨戒釋相.docx"
d = Document(p)
ps = [x.text for x in d.paragraphs]
print(len(ps))
K2, K3 = 904, 1656
seg = ps[K2:K3]
out = io.open(B + r"\_tmp_jz2\hui_ben_slice.txt", "w", encoding="utf-8")
for i, t in enumerate(seg):
    out.write("%04d\t%s\n" % (K2 + i, t[:120].replace("\n", " ")))
out.close()
print("slice", len(seg))
# tag stats
import collections
c = collections.Counter()
for t in seg:
    m = re.match(r'^【(鈔|記)(\d*)】', t)
    if m: c[m.group(1)] += 1
print(c)
