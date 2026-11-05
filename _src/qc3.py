
# -*- coding: utf-8 -*-
import os, io, re
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
def load(tag):
    S = os.path.join(B,'TXT_分卷',tag); T = os.path.join(B,'AI語譯','out',tag)
    out = []
    for f in sorted(os.listdir(S)):
        if not f.endswith('.txt'): continue
        key = f[:-4]; p = os.path.join(T, key+'.txt')
        if not os.path.exists(p): continue
        sp = [x.strip() for x in io.open(os.path.join(S,f),encoding='utf-8').read().split('\n')[5:] if x.strip()]
        tp = [x.strip() for x in re.split(r'\n\s*\n', io.open(p,encoding='utf-8').read()) if x.strip()]
        out.append((key, sp, tp))
    return out
WEN = re.compile(r'[之乎者也矣焉哉]')
rows = []
for tag in ['02_戒疏','04_比丘尼鈔','03_業疏']:
    for key, sp, tp in load(tag):
        for i in range(min(len(sp), len(tp))):
            o, t = sp[i], tp[i]
            if len(o) < 40: continue
            if len(t) < 0.5*len(o):
                rows.append((tag, key, i, 'SHORT', o, t))
            elif len(WEN.findall(t))/max(1,len(t)) > 0.12:
                rows.append((tag, key, i, 'WEN', o, t))
out = os.path.join(B,'AI語譯','_work','qc_report.tsv')
with io.open(out,'w',encoding='utf-8') as fh:
    for r in rows:
        fh.write('\t'.join([r[0], r[1], str(r[2]), r[3], r[4].replace('\n',' '), r[5].replace('\n',' ')]) + '\n')
print('rows', len(rows))
