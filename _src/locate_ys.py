
# -*- coding: utf-8 -*-
import os, io, json, re, sys
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
SRC = os.path.join(B,'TXT_分卷','03_業疏'); TR = os.path.join(B,'AI語譯','out','03_業疏'); RV = os.path.join(B,'AI語譯','review_業疏')
rows = []
for f in sorted(os.listdir(RV)):
    if not f.endswith('.json'): continue
    key = f[:-5]
    sp = [x.strip() for x in io.open(os.path.join(SRC,key+'.txt'),encoding='utf-8').read().split('\n')[5:] if x.strip()]
    tp = [x.strip() for x in re.split(r'\n\s*\n', io.open(os.path.join(TR,key+'.txt'),encoding='utf-8').read()) if x.strip()]
    arr = json.load(io.open(os.path.join(RV,f),encoding='utf-8'))
    for it in arr:
        q = str(it.get('quote','')).strip()
        idx = -1
        for i,s in enumerate(sp):
            if q and q in s: idx = i; break
        tv = tp[idx] if 0 <= idx < len(tp) else ''
        rows.append((key, idx, q, tv, str(it.get('kind','')), str(it.get('issue','')), str(it.get('fix',''))))
out = os.path.join(B,'AI語譯','_work','ys_issues.tsv')
with io.open(out,'w',encoding='utf-8') as fh:
    for r in rows:
        fh.write('\t'.join([r[0], str(r[1]), r[2], r[3].replace('\t',' '), r[4], r[5].replace('\t',' '), r[6].replace('\t',' ')]) + '\n')
print('rows', len(rows), 'located', sum(1 for r in rows if r[1] >= 0))
