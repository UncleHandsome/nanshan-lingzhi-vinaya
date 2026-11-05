
# -*- coding: utf-8 -*-
import io, os, re
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
S = os.path.join(D,'TXT_分卷','03_業疏')
pairs = [('門䦘','門閫'),('䊩汁','潘汁'),('安放有二','安得有二')]
n=0
for f in sorted(os.listdir(S)):
    if not f.endswith('.txt'): continue
    p=os.path.join(S,f); t=io.open(p,encoding='utf-8').read(); b=t
    for a,c in pairs: t=t.replace(a,c)
    t=re.sub(r'\s+㝢\s+','宇',t)
    if t!=b:
        io.open(p,'w',encoding='utf-8').write(t); n+=1
print('files',n)
