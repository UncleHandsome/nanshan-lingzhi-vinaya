
# -*- coding: utf-8 -*-
import io, os, json, re
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
RV = os.path.join(D,'AI語譯','review_low_all')
def clean(s):
    s=(s or '').strip()
    s=re.sub(r'^(應譯為|可譯為|宜譯為|譯為|改譯為|應改為|改為|補譯為)[：:]?','',s).strip()
    return s.strip('「」『』')
f='01_行事鈔__08b_卷中之四.json'
book,key=f[:-5].split('__',1)
p=os.path.join(D,'AI語譯','out',book,key+'.txt')
t=io.open(p,encoding='utf-8').read()
arr=json.load(io.open(os.path.join(RV,f),encoding='utf-8'))
n=0; miss=[]
for it in arr:
    q=(it.get('quote') or '').strip(); fx=clean(it.get('fix'))
    if not q or len(fx)<8: continue
    if it.get('kind')=='增譯': continue
    if q in t:
        t=t.replace(q,fx,1); n+=1; continue
    head=q[:12]
    if head in t:
        i=t.index(head); j=t.find('。',i)
        if j<0: j=t.find('\n\n',i)
        if j<0: j=len(t)
        t=t[:i]+fx+t[j+1:]
        n+=1
    else:
        miss.append(q[:14])
io.open(p,'w',encoding='utf-8').write(t)
print('applied',n,'of',len(arr),'miss',miss[:4])
