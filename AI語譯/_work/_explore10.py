import sys,os
sys.path.insert(0, r"C:\Users\lionc\OneDrive\桌面\XW\三大部")
from docx import Document
p=r"C:\Users\lionc\OneDrive\桌面\XW\三大部\白話\會本_篇13_篇聚名報.docx"
d=Document(p)
ps=[x for x in d.paragraphs]
print("paras:",len(ps))
for i,x in enumerate(ps[:60]):
    t=x.text.strip()
    if t: print(i, repr(t[:90]))
