
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
raw=io.open(p,encoding='utf-8').read()
sep='\r\n\r\n' if '\r\n\r\n' in raw else '\n\n'
paras=re.split(r'\r?\n\r?\n', raw)
arr=json.load(io.open(os.path.join(RV,f),encoding='utf-8'))
n=0
for it in arr:
    seg=int(it.get('seg') or 0); fx=clean(it.get('fix')); kind=it.get('kind') or ''
    if seg<1 or seg>len(paras) or len(fx)<6 or kind!='漏譯': continue
    txt=paras[seg-1]
    if fx in txt: continue
    iss=it.get('issue') or ''
    if ('標題' in iss) and ('段末' not in iss):
        paras[seg-1]=fx+txt
    else:
        sepch='' if txt.rstrip().endswith(('。','」')) else '。'
        paras[seg-1]=txt+sepch+fx
    n+=1
io.open(p,'w',encoding='utf-8').write(sep.join(paras))
print('paras',len(paras),'applied',n)
