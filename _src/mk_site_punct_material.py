# -*- coding: utf-8 -*-
"""從目前網站頁面收集真正無句讀的 pair。"""
import io, os, re
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
BOOKS = {'行事鈔':('xingshichao',['卷上','卷中','卷下']),'戒疏':('jieshu',['卷一','卷二','卷三','卷四']),'業疏':('yeshu',['卷一','卷二','卷三','卷四']),'尼鈔':('nicao',['卷上','卷中','卷下']),'義鈔':('yichao',['卷上','卷中'])}
items=[]; seen=set(); counts={}
for name,(book,vols) in BOOKS.items():
    for v in vols:
        p=os.path.join(B,'docs',book,v+'.html')
        if not os.path.exists(p): continue
        t=io.open(p,encoding='utf-8').read()
        for m in re.finditer(r'<div class="o[^"]*">(.*?)</div>',t,re.S):
            x=re.sub('<[^>]+>','',m.group(1)).strip()
            body=re.sub(r'^【[^】]+】','',x).strip()
            n=len(re.findall(r'[\u4e00-\u9fff]',body)); pu=len(re.findall(r'[，。；：！？、]',body))
            if n>30 and pu/n<0.01 and body not in seen:
                seen.add(body); items.append((name,v,body)); counts[name]=counts.get(name,0)+1
H='''# 五書網站無句讀待補

## 輸出檔名
```text
句讀待補_全部_回.md
```

## 任務
只補句讀，不改字、不增刪、不翻譯。

- 保留所有漢字與順序
- 只加入：，。；：！？、「」『』（）
- 每段輸出：
```text
## P編號
原文（已加句讀）
```

---
'''
txt=H
for i,(book,v,body) in enumerate(items,1):
    txt+='\n## P%03d\n\n- 書：%s\n- 卷：%s\n- 字數：%d\n\n%s\n'%(i,book,v,len(re.findall(r'[\u4e00-\u9fff]',body)),body)
p=os.path.join(B,'重作材料_長段','句讀待補_全部.md')
io.open(p,'w',encoding='utf-8').write(txt)
print('total',len(items),counts)
