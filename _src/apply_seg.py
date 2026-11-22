# -*- coding: utf-8 -*-
"""解析 seg.txt：把三組輸出按原文起點分回 GAP06/13/14，再套用。"""
import io,re,json,os
B=r'C:\Users\lionc\OneDrive\桌面\XW\三大部'; t=io.open(os.path.join(B,'重作材料_長段','seg.txt'),encoding='utf-8').read()
def han(s): return ''.join(re.findall(r'[\u4e00-\u9fff]',str(s)))
secs=[]
for m in re.finditer(r'(?m)^##\s+(.+?)\s*\n(.*?)(?=^## |\Z)',t,re.S):
    b=m.group(2); a=re.search(r'^原文起：(.+)$',b,re.M); c=re.search(r'^白話起：(.+)$',b,re.M)
    if a and c: secs.append((a.group(1).strip(),c.group(1).strip()))
print('sections',len(secs))
rows=[json.loads(x) for x in io.open(os.path.join(B,'定稿','yichao.jsonl'),encoding='utf-8') if x.strip()]
keys=['GAP06','GAP13','GAP14']
groups={k:[] for k in keys}
for s,tr in secs:
    hh=han(s)[:8]; found=None
    for k in keys:
        r=next(r for r in rows if r['key']==k)
        if hh and hh in han(r['source']): found=k;break
    if found: groups[found].append((s,tr))
    else: print('UNMATCHED',s[:20])
for k in keys:
    g=groups[k]; print(k,len(g))
    if not g: continue
    r=next(r for r in rows if r['key']==k); S=r['source'];T=r['translation']
    spos=[];cur=0
    for s,tr in g:
        i=S.find(s,cur)
        if i<0: print('miss src',k,s); spos=[];break
        spos.append(i);cur=i+1
    tpos=[];cur=0
    for s,tr in g:
        i=T.find(tr,cur)
        if i<0: print('miss tr',k,tr); tpos=[];break
        tpos.append(i);cur=i+1
    if len(spos)!=len(g) or len(tpos)!=len(g): continue
    new=[];a0=r['raw_start']
    # raw 對照
    raw=io.open(os.path.join(B,'TXT','05_四分律拾毗尼義鈔.txt'),encoding='utf-8').read(); h='';mp=[]
    for i,c in enumerate(raw):
        if '\u4e00'<=c<='\u9fff': h+=c;mp.append(i)
    for j in range(len(g)):
        se=spos[j+1] if j+1<len(spos) else len(S); te=tpos[j+1] if j+1<len(tpos) else len(T)
        ss=S[spos[j]:se].strip(); tt=T[tpos[j]:te].strip(); sh=han(ss); q=h.find(sh,a0); e=q+len(sh); a0=e
        nr=dict(r); nr['key']=k+'-%d'%(j+1); nr['source']=raw[mp[q]:mp[e-1]+1].strip(); nr['translation']=tt; nr['raw_start']=q; nr['raw_end']=e
        nr['segments']=[{'label':r.get('label','鈔文'),'source':nr['source'],'translation':tt}]
        new.append(nr)
    idx=rows.index(r); rows[idx:idx+1]=new; print('applied',k,len(new))
io.open(os.path.join(B,'定稿','yichao.jsonl'),'w',encoding='utf-8').writelines(json.dumps(r,ensure_ascii=False)+'\n' for r in rows)
