
# -*- coding: utf-8 -*-
import io, os, re
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
base = os.path.join(D,'AI語譯','out','02_戒疏')
m = {'【疏】':'【疏文】','【律】':'【律文】','【註】':'【註文】','【記】':'【記文】'}
n=0
for f in sorted(os.listdir(base)):
    if not f.endswith('.txt'): continue
    p=os.path.join(base,f); t=io.open(p,encoding='utf-8').read(); b=t
    for a,c in m.items():
        t = re.sub('(^|\n\n)' + re.escape(a), lambda mm: mm.group(1)+c, t)
    if t!=b: io.open(p,'w',encoding='utf-8').write(t); n+=1
print('files', n)
