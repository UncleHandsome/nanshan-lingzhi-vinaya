
# -*- coding: utf-8 -*-
import os, io, re
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
BOOKS = [('01_行事鈔','01_行事鈔'),('03_業疏','03_業疏'),('02_戒疏','02_戒疏'),
         ('04_比丘尼鈔','04_比丘尼鈔'),('資持記','資持記_細分'),('05_拾毗尼義鈔','05_拾毗尼義鈔')]
WEN = re.compile(r'[之乎者也矣焉哉]')
rows = []
for tag, src in BOOKS:
    S = os.path.join(B,'TXT_分卷',src); O = os.path.join(B,'AI語譯','out',tag)
    if not os.path.isdir(O): continue
    for f in sorted(os.listdir(S)):
        if not f.endswith('.txt'): continue
        key = f[:-4]; p = os.path.join(O, key+'.txt')
        if not os.path.exists(p): continue
        raw = io.open(os.path.join(S,f),encoding='utf-8').read().split('\n')[5:]
        spP = [x for x in re.split(r'\n\s*\n', '\n'.join(raw)) if x.strip()]
        spL = [x for x in raw if x.strip()]
        sp = spP if len(spP) >= len(spL) else spL
        tp = [x.strip() for x in re.split(r'\n\s*\n', io.open(p,encoding='utf-8').read()) if x.strip()]
        for i in range(min(len(sp), len(tp))):
            o, t = sp[i].strip(), tp[i]
            if len(o) < 40: continue
            if t == o:
                rows.append((tag,key,i,'IDENT',o,t)); continue
            if len(t) < 0.5*len(o):
                rows.append((tag,key,i,'SHORT',o,t)); continue
            if len(WEN.findall(t))/max(1,len(t)) > 0.12:
                rows.append((tag,key,i,'WEN',o,t)); continue
            if '〔註〕' in t or '〔注〕' in t:
                rows.append((tag,key,i,'EMPTYNOTE',o,t))
out = os.path.join(B,'AI語譯','_work','qc_all.tsv')
with io.open(out,'w',encoding='utf-8') as fh:
    for r in rows:
        fh.write('\t'.join([r[0],r[1],str(r[2]),r[3],r[4].replace('\n',' '),r[5].replace('\n',' ')])+'\n')
from collections import Counter
print('total', len(rows), Counter(r[3] for r in rows))
print('by book', Counter(r[0] for r in rows))
