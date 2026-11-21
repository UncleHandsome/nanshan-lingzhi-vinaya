# -*- coding: utf-8 -*-
"""用 TXT_句讀校定 設定 display_source，不改 source。"""
import io, json, os, re
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
def han(s): return ''.join(re.findall(r'[\u4e00-\u9fff]', str(s)))
for book in ('yeshu','nicao','yichao'):
    t=io.open(os.path.join(B,'TXT_句讀校定',book+'.txt'),encoding='utf-8').read()
    hc=''; mc=[]
    for i,c in enumerate(t):
        if '\u4e00'<=c<='\u9fff': hc+=c; mc.append(i)
    p=os.path.join(B,'定稿',book+'.jsonl')
    rows=[json.loads(x) for x in io.open(p,encoding='utf-8') if x.strip()]
    hit=seg_hit=0
    for r in rows:
        a,b=r.get('raw_start',-1),r.get('raw_end',-1)
        if a<0 or b<=a: continue
        r['display_source']=t[mc[a]:mc[b-1]+1]; hit+=1
        cur=a
        for s in r.get('segments') or []:
            sh=han(s.get('source','')); q=hc.find(sh,cur)
            if q>=0:
                s['display_source']=t[mc[q]:mc[q+len(sh)-1]+1]; seg_hit+=1; cur=q+len(sh)
    io.open(p,'w',encoding='utf-8').writelines(json.dumps(r,ensure_ascii=False)+'\n' for r in rows)
    print(book,'rows',len(rows),'row_display',hit,'seg_display',seg_hit)
