# -*- coding: utf-8 -*-
"""從業疏頁面收集真正無句讀的原文，產補句讀材料。"""
import io, os, re
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
items=[]; seen=set()
for v in ('卷一','卷二','卷三','卷四'):
    t=io.open(os.path.join(B,'docs','yeshu',v+'.html'),encoding='utf-8').read()
    for m in re.finditer(r'<div class="o[^"]*">(.*?)</div>',t,re.S):
        x=re.sub('<[^>]+>','',m.group(1)); body=re.sub(r'^【[^】]+】','',x).strip()
        n=len(re.findall(r'[\u4e00-\u9fff]',body)); p=len(re.findall(r'[，。；：！？、]',body))
        if n>30 and p/max(1,n)<0.01 and body not in seen:
            seen.add(body); items.append((v,body))
H='''# 業疏 補句讀（71 段）

## 輸出檔名
```text
業疏_句讀補漏_回.md
```

## 任務
只補句讀，不改字、不增刪、不翻譯。

- 保留所有漢字，順序不變
- 只加入：，。；：！？、「」『』（）
- 不加入任何新詞或解釋
- 每段輸出：
```text
## 業疏-P編號
原文（已加句讀）
```

---
'''
txt=H
for i,(v,body) in enumerate(items,1):
    txt+='\n## 業疏-P%02d\n\n- 出處：%s\n\n%s\n'%(i,v,body)
p=os.path.join(B,'重作材料_長段','業疏_句讀補漏_71.md')
io.open(p,'w',encoding='utf-8').write(txt)
print('items',len(items),'->',p)
