# -*- coding: utf-8 -*-
"""把長段/GAP回覆的起迄標記套回定稿，切成多列。"""
import io,json,re,os,shutil
B=r'C:\Users\lionc\OneDrive\桌面\XW\三大部'; BK=os.path.join(B,'定稿','_備份_套用長段'); os.makedirs(BK,exist_ok=True)
def han(s): return ''.join(re.findall(r'[\u4e00-\u9fff]',str(s)))
def parse_starts(t,key):
    src=[]; tr=[]
    for m in re.finditer(r'^##\s+%s-\d+\s*\n(.*?)(?=^## |\Z)'%re.escape(key),t,re.M|re.S):
        blk=m.group(1)
        a=re.search(r'^原文起：(.+)$',blk,re.M); b=re.search(r'^白話起：(.+)$',blk,re.M)
        if a: src.append(a.group(1).strip())
        if b: tr.append(b.group(1).strip())
    return src,tr
def split_row(r,key,t):
    src,tr=parse_starts(t,key)
    if len(src)<2 or len(tr)<2: return None
    if any(x.startswith('（現譯從缺') or x.startswith('(現譯從缺') for x in tr): return None
    S=r.get('source',''); T=r.get('translation','')
    spos=[]; cur=0
    for m in src:
        i=S.find(m,cur)
        if i<0: return None
        spos.append(i); cur=i+1
    tpos=[]; cur=0
    for m in tr:
        i=T.find(m,cur)
        if i<0: return None
        tpos.append(i); cur=i+1
    # 以每個起點為邊界，最後補到結尾
    out=[]; n=len(spos)
    for k,(a,b) in enumerate(zip(spos,tpos)):
        se=spos[k+1] if k+1<n else len(S)
        te=tpos[k+1] if k+1<n else len(T)
        ss=S[a:se].strip(); tt=T[b:te].strip()
        if not ss or not tt: return None
        out.append((ss,tt))
    return out

# 載入五書
data={}
for book in ('xingshichao','jieshu','yeshu','nicao','yichao'):
    p=os.path.join(B,'定稿',book+'.jsonl'); shutil.copy(p,os.path.join(BK,book+'.jsonl'))
    data[book]=[json.loads(x) for x in io.open(p,encoding='utf-8') if x.strip()]
# L 編號→row
items=[]
for book in ('xingshichao','jieshu','yeshu','nicao','yichao'):
    for r in data[book]:
        if len(han(r.get('source','')))>500: items.append((book,r))
Lmap={('%03d'%i):x for i,x in enumerate(items,1)}
d=os.path.join(B,'測試','重譯','_長段_送千問','回覆'); applied=0; kept=0
for fn in sorted(os.listdir(d)):
    m=re.match(r'^L(\d+)_回\.txt$',fn)
    if not m: continue
    num=m.group(1); t=io.open(os.path.join(d,fn),encoding='utf-8').read()
    book,row=Lmap.get(num,(None,None))
    if row is None: continue
    segs=split_row(row,'L'+num,t)
    if not segs: kept+=1; continue
    new=[]
    for i,(ss,tt) in enumerate(segs,1):
        nr=dict(row); nr['key']=row['key']+'-%d'%i; nr['source']=ss; nr['translation']=tt
        nr['segments']=[{'label':row.get('label','疏文'),'source':ss,'translation':tt}]
        new.append(nr)
    idx=data[book].index(row); data[book][idx:idx+1]=new; applied+=1
print('long applied',applied,'kept',kept)
# GAP
d2=os.path.join(B,'測試','重譯','_義鈔GAP_送千問','回覆'); gapp=0
for fn in sorted(os.listdir(d2)):
    m=re.match(r'^(GAP\d+)_回\.txt$',fn)
    if not m: continue
    key=m.group(1); t=io.open(os.path.join(d2,fn),encoding='utf-8').read()
    row=next((r for r in data['yichao'] if r['key']==key),None)
    if not row: continue
    segs=split_row(row,key,t)
    if not segs: continue
    new=[]
    for i,(ss,tt) in enumerate(segs,1):
        nr=dict(row); nr['key']=key+'-%d'%i; nr['source']=ss; nr['translation']=tt
        nr['segments']=[{'label':row.get('label','鈔文'),'source':ss,'translation':tt}]
        new.append(nr)
    idx=data['yichao'].index(row); data['yichao'][idx:idx+1]=new; gapp+=1
print('gap applied',gapp)
for book,rows in data.items():
    io.open(os.path.join(B,'定稿',book+'.jsonl'),'w',encoding='utf-8').writelines(json.dumps(r,ensure_ascii=False)+'\n' for r in rows)
