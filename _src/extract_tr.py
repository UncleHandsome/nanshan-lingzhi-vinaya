
# -*- coding: utf-8 -*-
import io, os, re
from docx import Document
from docx.oxml.ns import qn
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
S = os.path.join(D,'TXT_分卷','03_業疏')
files = sorted([f for f in os.listdir(S) if f.endswith('.txt')], key=lambda x:(0 if x.startswith('00_') else 1,x))
counts=[]; 
for f in files:
    sp=[x.strip() for x in io.open(os.path.join(S,f),encoding='utf-8').read().split('\n')[5:] if x.strip()]
    counts.append((f[:-4], len(sp)))
print('chunks', len(counts), 'total', sum(c for _,c in counts))
def shaded(p):
    return p._p.find('.//'+qn('w:shd')) is not None
trs=[]
for vol in ['卷一','卷二','卷三','卷四']:
    p=os.path.join(D,'白話','業疏_%s_白話對照本.docx'%vol)
    d=Document(p)
    for para in d.paragraphs:
        t=para.text.strip()
        if not t: continue
        if shaded(para): continue
        if para.style.name.startswith('Heading'): continue
        if len(t) < 4: continue
        trs.append(t)
print('collected 譯文', len(trs))
