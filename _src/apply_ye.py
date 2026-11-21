# -*- coding: utf-8 -*-
"""套用 ye.txt 的業疏三段譯文。"""
import io, json, os, re
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
raw = io.open(os.path.join(B,'TXT','03_四分律刪補隨機羯磨疏.txt'),encoding='utf-8').read(); h='';mp=[]
for i,c in enumerate(raw):
    if '\u4e00'<=c<='\u9fff': h+=c;mp.append(i)
def han(s): return ''.join(re.findall(r'[\u4e00-\u9fff]',str(s)))
t=io.open(os.path.join(B,'重作材料_長段','ye.txt'),encoding='utf-8').read()
spans={'01':(6836,7902),'02':(28135,28221),'03':(287447,287741)}
rows=[json.loads(x) for x in io.open(os.path.join(B,'定稿','yeshu.jsonl'),encoding='utf-8') if x.strip()]
rows=[r for r in rows if not r['key'].startswith('YE-')]
for g,(a,b) in spans.items():
    m=re.search(r'## 業疏-G%s\s*\n(.*?)(?=^## |\Z)'%g,t,re.M|re.S)
    blocks=[x.strip() for x in re.split(r'\n\s*\n',m.group(1)) if x.strip()]
    trs=[]
    for blk in blocks:
        body=re.sub(r'^(?:【[^】]+】\s*)+','',blk).strip(); bh=han(body)
        if not bh: continue
        if h.find(bh[:20])>=0 or h.find(bh[:12])>=0: continue
        trs.append(body)
    tr='\n'.join(trs).strip()
    src=raw[mp[a]:mp[b-1]+1].strip()
    rows.append({'book':'業疏','book_id':'yeshu','key':'YE-G'+g,'label':'記文','source':src,
                 'translation':tr,'revised':True,'segments':[{'label':'記文','source':src,'translation':tr}],
                 'raw_start':a,'raw_end':b,'vol':'','chunk':''})
io.open(os.path.join(B,'定稿','yeshu.jsonl'),'w',encoding='utf-8').writelines(json.dumps(r,ensure_ascii=False)+'\n' for r in rows)
print('rows',len(rows))
