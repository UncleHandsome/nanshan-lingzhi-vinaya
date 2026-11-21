# -*- coding: utf-8 -*-
"""套用 ju.txt 的 98 段句讀，只寫 display_source。"""
import io,json,re,os
B=r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
def han(s): return ''.join(re.findall(r'[\u4e00-\u9fff]',str(s)))
t=io.open(os.path.join(B,'重作材料_長段','ju.txt'),encoding='utf-8').read()
items=[]
for m in re.finditer(r'(?m)^## (P\d+)\s*\n(.*?)(?=^## |\Z)',t,re.S):
    body=m.group(2).strip()
    if body: items.append((m.group(1),body))
print('items',len(items))
data={}
idx=[]
for book in ('xingshichao','jieshu','yeshu','nicao','yichao'):
    p=os.path.join(B,'定稿',book+'.jsonl')
    rows=[json.loads(x) for x in io.open(p,encoding='utf-8') if x.strip()]
    data[book]=(p,rows)
    for r in rows:
        segs=r.get('segments') or []
        if segs:
            for s in segs:
                hh=han(s.get('source',''))
                if hh: idx.append((hh,s,r,False))
        else:
            hh=han(r.get('source',''))
            if hh: idx.append((hh,r,r,True))
hit=0; miss=[]
for pid,body in items:
    hh=han(body); found=False
    for oh,s,r,single in idx:
        if oh==hh:
            s['display_source']=body
            if single: r['display_source']=body
            hit+=1; found=True; break
    if not found: miss.append(pid)
for book,(p,rows) in data.items():
    io.open(p,'w',encoding='utf-8').writelines(json.dumps(r,ensure_ascii=False)+'\n' for r in rows)
print('hit',hit,'miss',len(miss),miss[:20])
