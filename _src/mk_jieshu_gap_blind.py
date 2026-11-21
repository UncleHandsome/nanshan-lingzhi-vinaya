# -*- coding: utf-8 -*-
import io, json, os, re
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
raw = io.open(os.path.join(B,'TXT','02_四分律含注戒本疏.txt'),encoding='utf-8').read(); h='';mp=[]
for i,c in enumerate(raw):
    if '\u4e00'<=c<='\u9fff': h+=c;mp.append(i)
def nonbody(t):
    t=t[:140]
    if t.startswith(('大覺慈父','九十單提法','百眾學法','四分戒本》者','甞聞毗尼藏','原夫大雄','疏卷第一')): return True
    if '【四分律' in t[:80] and '卷' in t[:100]: return True
    if '四分律含注戒本疏卷' in t[:50] or '行宗記卷' in t[:60]: return True
    if re.match(r'^[一二三四五六七八九十百]+[^。]{0,30}戒',t): return True
    if t.startswith(('四分律刪補','四分律含注','四分律拾毗尼','四分律比丘尼鈔','南山三大部','底本')): return True
    if '篇第' in t[:80] and ('】' in t[:80] or '卷' in t[:60]): return True
    return False
rows=[json.loads(x) for x in io.open(os.path.join(B,'定稿','jieshu.jsonl'),encoding='utf-8') if x.strip()]; iv=[(r['raw_start'],r['raw_end']) for r in rows if r.get('raw_start',-1)>=0]
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
H='''# 戒疏 正文缺口盲翻（15 段）

## 輸出檔名
```text
戒疏_缺口盲翻_15_回.md
```

## 任務
逐段盲翻。每段輸出：
```text
## 戒疏-G01
【段別】原文
【段別】白話
```
- 不改字、不增刪
- 不參考現譯
- 段別：疏文／記文／註文／律文／序文；不確定用【疏文】
- 單段超過 500 字，依段落、科判、問答起訖切小段
- 原文開頭若只剩「疏】」「註】」標籤，照原樣保留，不要自行補字

---
'''
txt=H
for n,(a,b) in enumerate(gaps,1):
    s=raw[mp[a]:mp[b-1]+1].strip()
    txt+='\n## 戒疏-G%02d\n\n- raw：%d–%d\n- 字數：%d\n\n【原文】\n\n%s\n'%(n,a,b,b-a,s)
p=os.path.join(B,'重作材料_長段','戒疏_缺口盲翻_15.md')
io.open(p,'w',encoding='utf-8').write(txt)
print('gaps',len(gaps),p)
