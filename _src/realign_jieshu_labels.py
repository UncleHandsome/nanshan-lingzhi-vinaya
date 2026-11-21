# -*- coding: utf-8 -*-
"""戒疏：source 允許 raw 夾行內段標（疏記律註鈔）時，用去標序列定位再映射回 raw。"""
import io, json, os, re, shutil
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
raw = io.open(os.path.join(B,'TXT','02_四分律含注戒本疏.txt'),encoding='utf-8').read(); h='';mp=[]
for i,c in enumerate(raw):
    if '\u4e00'<=c<='\u9fff': h+=c;mp.append(i)
skip=set('疏記律註鈔'); h2=''; m2=[]
for i,c in enumerate(h):
    if c not in skip: h2+=c; m2.append(i)
p=os.path.join(B,'定稿','jieshu.jsonl')
shutil.copy(p,os.path.join(B,'定稿','_舊_jieshu_before_labels.jsonl'))
rows=[json.loads(x) for x in io.open(p,encoding='utf-8') if x.strip()]
fixed=miss=0
for r in rows:
    s=''.join(re.findall(r'[\u4e00-\u9fff]',r.get('source','')))
    if not s: continue
    q=h.find(s)
    if q<0:
        q2=h2.find(s)
        if q2>=0:
            q=m2[q2]; e=m2[q2+len(s)-1]+1
        else:
            miss+=1; continue
    else:
        e=q+len(s)
    r['raw_start']=q; r['raw_end']=e; fixed+=1
io.open(p,'w',encoding='utf-8').writelines(json.dumps(r,ensure_ascii=False)+'\n' for r in rows)
print('fixed',fixed,'miss',miss)
