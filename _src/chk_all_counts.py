
# -*- coding: utf-8 -*-
import os, io, re
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
BOOKS = [('01_行事鈔','01_行事鈔'),('03_業疏','03_業疏'),('02_戒疏','02_戒疏'),
         ('04_比丘尼鈔','04_比丘尼鈔'),('資持記','資持記_細分'),('05_拾毗尼義鈔','05_拾毗尼義鈔')]
for tag, src in BOOKS:
    S=os.path.join(B,'TXT_分卷',src); O=os.path.join(B,'AI語譯','out',tag)
    bad=[]; n=0
    for f in sorted(os.listdir(S)):
        if not f.endswith('.txt'): continue
        key=f[:-4]; p=os.path.join(O,key+'.txt')
        if not os.path.exists(p): continue
        n+=1
        raw=io.open(os.path.join(S,f),encoding='utf-8').read().split('\n')[5:]
        spP=len([x for x in re.split(r'\n\s*\n','\n'.join(raw)) if x.strip()])
        spL=len([x for x in raw if x.strip()])
        tp=len([x for x in re.split(r'\r?\n\r?\n', io.open(p,encoding='utf-8').read()) if x.strip()])
        if tp!=spP and tp!=spL: bad.append((key, spP, spL, tp))
    print(tag, 'chunks', n, 'mismatch', len(bad))
    for b in bad[:5]: print('   ', b)
