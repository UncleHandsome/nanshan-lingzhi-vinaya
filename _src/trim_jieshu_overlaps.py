# -*- coding: utf-8 -*-
"""戒疏 label 對齊後，裁掉重疊並把 source 改成 raw 切片。"""
import io, json, os, re
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
raw = io.open(os.path.join(B,'TXT','02_四分律含注戒本疏.txt'),encoding='utf-8').read(); h='';mp=[]
for i,c in enumerate(raw):
    if '\u4e00'<=c<='\u9fff': h+=c;mp.append(i)
p=os.path.join(B,'定稿','jieshu.jsonl')
rows=[json.loads(x) for x in io.open(p,encoding='utf-8') if x.strip()]
rows=[r for r in rows if r.get('raw_start',-1)>=0]; rows.sort(key=lambda r:(r['raw_start'],r['raw_end']))
keep=[]; last=0
for r in rows:
    a,b=r['raw_start'],r['raw_end']
    if a<last: a=last
    if b<=a: continue
    r['raw_start']=a; r['raw_end']=b; r['source']=raw[mp[a]:mp[b-1]+1].strip(); keep.append(r); last=b
io.open(p,'w',encoding='utf-8').writelines(json.dumps(x,ensure_ascii=False)+'\n' for x in keep)
print('rows',len(keep))
