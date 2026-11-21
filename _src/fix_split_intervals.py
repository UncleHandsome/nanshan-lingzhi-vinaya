# -*- coding: utf-8 -*-
"""修正切段後仍共用舊 raw 區間的問題。"""
import io,json,re,os
B=r'C:\Users\lionc\OneDrive\桌面\XW\三大部'; RAW={
 'xingshichao':'TXT/01_四分律刪繁補闕行事鈔.txt','jieshu':'TXT/02_四分律含注戒本疏.txt',
 'yeshu':'TXT/03_四分律刪補隨機羯磨疏.txt','nicao':'TXT/04_四分律比丘尼鈔.txt','yichao':'TXT/05_四分律拾毗尼義鈔.txt'}
def han(s): return ''.join(re.findall(r'[\u4e00-\u9fff]',str(s)))
for book,path in RAW.items():
    raw=io.open(os.path.join(B,path),encoding='utf-8').read(); h=''; mp=[]
    for i,c in enumerate(raw):
        if '\u4e00'<=c<='\u9fff': h+=c; mp.append(i)
    p=os.path.join(B,'定稿',book+'.jsonl'); rows=[json.loads(x) for x in io.open(p,encoding='utf-8') if x.strip()]
    groups={}
    for r in rows:
        if r.get('raw_start',-1)>=0: groups.setdefault((r['raw_start'],r['raw_end']),[]).append(r)
    fixed=0; miss=0
    for (a,b),g in groups.items():
        if len(g)<2: continue
        cur=a
        for r in g:
            sh=han(r.get('source',''))
            if not sh: continue
            q=h.find(sh,cur,b)
            if q<0:
                q=h.find(sh,a,b)
                if q<0: miss+=1; continue
            e=q+len(sh)
            r['raw_start']=q; r['raw_end']=e; r['source']=raw[mp[q]:mp[e-1]+1].strip()
            if r.get('segments'): r['segments'][0]['source']=r['source']
            cur=e; fixed+=1
    io.open(p,'w',encoding='utf-8').writelines(json.dumps(r,ensure_ascii=False)+'\n' for r in rows)
    print(book,'fixed',fixed,'miss',miss)
