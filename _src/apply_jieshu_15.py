# -*- coding: utf-8 -*-
"""套用戒疏 15 缺口盲翻回覆。"""
import io, json, os, re
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
raw = io.open(os.path.join(B,'TXT','02_四分律含注戒本疏.txt'),encoding='utf-8').read(); h='';mp=[]
for i,c in enumerate(raw):
    if '\u4e00'<=c<='\u9fff': h+=c;mp.append(i)
def han(s): return ''.join(re.findall(r'[\u4e00-\u9fff]',str(s)))
def nonbody(t):
    t=t[:140]
    if t.startswith(('大覺慈父','九十單提法','百眾學法','四分戒本》者','甞聞毗尼藏','原夫大雄','疏卷第一')): return True
    if '【四分律' in t[:80] and '卷' in t[:100]: return True
    if '四分律含注戒本疏卷' in t[:50] or '行宗記卷' in t[:60]: return True
    if re.match(r'^[一二三四五六七八九十百]+[^。]{0,30}戒',t): return True
    if t.startswith(('四分律刪補','四分律含注','四分律拾毗尼','四分律比丘尼鈔','南山三大部','底本')): return True
    if '篇第' in t[:80] and ('】' in t[:80] or '卷' in t[:60]): return True
    return False
p=os.path.join(B,'定稿','jieshu.jsonl')
rows=[json.loads(x) for x in io.open(p,encoding='utf-8') if x.strip()]
iv=[(r['raw_start'],r['raw_end']) for r in rows if r.get('raw_start',-1)>=0]
cover=[0]*len(h)
for a,b in iv:
    for i in range(a,min(b,len(h))): cover[i]+=1
gaps=[];i=0
while i<len(h):
    if cover[i]==0:
        j=i
        while j<len(h) and cover[j]==0:j+=1
        if j-i>=20 and not nonbody(raw[mp[i]:mp[i]+140]): gaps.append((i,j))
        i=j
    else:i+=1
t=io.open(os.path.join(B,'重作材料_長段','戒疏_缺口盲翻_15_回.md'),encoding='utf-8').read()
added=miss=0
for n,(a,b) in enumerate(gaps,1):
    m=re.search(r'## 戒疏-G%02d\s*\n(.*?)(?=^## |\Z)'%n,t,re.M|re.S)
    if not m: miss+=1; continue
    blocks=[x.strip() for x in re.split(r'\n\s*\n',m.group(1)) if x.strip()]
    srcs=[]; trs=[]
    for blk in blocks:
        body=re.sub(r'^(?:【[^】]+】\s*)+','',blk).strip(); bh=han(body)
        if not bh: continue
        # 原文必須能在這個缺口內找到
        if h.find(bh[:12],a,b)>=0:
            srcs.append((body,bh))
        else:
            trs.append(body)
    cur=a
    for k,(src,bh) in enumerate(srcs):
        q=h.find(bh[:12],cur,b)
        if q<0: miss+=1; continue
        e=q+len(bh)
        tr=trs[k] if k<len(trs) else (trs[-1] if trs else '')
        if not tr: miss+=1; continue
        rows.append({'book':'戒疏','book_id':'jieshu','key':'J15-G%02d-%d'%(n,k+1),'label':'疏文',
                     'source':raw[mp[q]:mp[e-1]+1].strip(),'translation':tr,'revised':True,
                     'segments':[{'label':'疏文','source':raw[mp[q]:mp[e-1]+1].strip(),'translation':tr}],
                     'raw_start':q,'raw_end':e,'vol':'','chunk':''})
        cur=e; added+=1
io.open(p,'w',encoding='utf-8').writelines(json.dumps(r,ensure_ascii=False)+'\n' for r in rows)
print('gaps',len(gaps),'added',added,'miss',miss,'rows',len(rows))
