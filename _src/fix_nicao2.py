
# -*- coding: utf-8 -*-
import io, os, re
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
O = os.path.join(D,'AI語譯','out')
reps = [('本篇大綱共分為十一門','本篇大綱共分為十門'),('以男內總有五尼','以界內總有五尼'),
        ('簡要釋五尼','簡要釋云：尼'),('慈悲誨誨指示','慈悲訓誨指示'),
        ('推𦙄','搥胸'),('𥢶𫝽','輭')]
n=0
for book in os.listdir(O):
    d=os.path.join(O,book)
    if not os.path.isdir(d): continue
    for f in sorted(os.listdir(d)):
        if not f.endswith('.txt'): continue
        p=os.path.join(d,f); t=io.open(p,encoding='utf-8').read(); b=t
        for a,c in reps: t=t.replace(a,c)
        t=re.sub(r'\[段數不合[^\]]*\]','',t)
        if t!=b: io.open(p,'w',encoding='utf-8').write(t); n+=1
print('files',n)
