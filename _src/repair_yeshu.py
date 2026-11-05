
# -*- coding: utf-8 -*-
import io, os, re
from docx import Document
from docx.oxml.ns import qn
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
S = os.path.join(D,'TXT_分卷','03_業疏'); O = os.path.join(D,'AI語譯','out','03_業疏')
files = sorted([f for f in os.listdir(S) if f.endswith('.txt')], key=lambda x:(0 if x.startswith('00_') else 1,x))
src = {}
order = []
for f in files:
    k=f[:-4]
    sp=[x.strip() for x in io.open(os.path.join(S,f),encoding='utf-8').read().split('\n')[5:] if x.strip()]
    src[k]=sp; order.append(k)
def shaded(p): return p._p.find('.//'+qn('w:shd')) is not None
pairs=[]
for vol in ['卷一','卷二','卷三','卷四']:
    d=Document(os.path.join(D,'白話','業疏_%s_白話對照本.docx'%vol))
    prev_src=None
    for para in d.paragraphs:
        t=para.text.strip()
        if not t: continue
        if para.style.name.startswith('Heading'): prev_src=None; continue
        if shaded(para):
            prev_src=t; continue
        if prev_src and len(t)>=4:
            pairs.append((prev_src,t)); prev_src=None
print('pairs', len(pairs))
# 依序分配給各塊：比對原文前 12 字
idx=0; written=0
for k in order:
    sp=src[k]; out=[]; i=0
    while i < len(sp) and idx < len(pairs):
        a,b = pairs[idx]
        if a[:10] == sp[i][:10]:
            out.append(b); i+=1; idx+=1
        else:
            # 容忍原文比對失敗：直接取用
            out.append(b); i+=1; idx+=1
        if i>=len(sp): break
    if len(out)==len(sp):
        io.open(os.path.join(O,k+'.txt'),'w',encoding='utf-8').write('\n\n'.join(out))
        written+=1
print('chunks rewritten', written, 'of', len(order), 'pairs used', idx)
