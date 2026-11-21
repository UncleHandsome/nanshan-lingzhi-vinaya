# -*- coding: utf-8 -*-
import io,json,re,os
B=r'C:\Users\lionc\OneDrive\桌面\XW\三大部'; rows=[json.loads(x) for x in io.open(os.path.join(B,'定稿','yichao.jsonl'),encoding='utf-8') if x.strip()]
def han(s): return ''.join(re.findall(r'[\u4e00-\u9fff]',str(s)))
items=[]; seen=set()
for r in rows:
 for s in (r.get('segments') or [{'label':r.get('label'),'source':r.get('source','')}]):
  src=s.get('source',''); n=len(han(src)); p=len(re.findall(r'[，。；：！？、]',src))
  if n>30 and p/n<0.01:
   hh=han(src)
   if hh in seen: continue
   seen.add(hh); items.append((r['key'],src))
H='''# 義鈔 句讀待補

## 輸出檔名
```text
義鈔_句讀待補_回.md
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
for i,(key,src) in enumerate(items,1):
 txt+='\n## P%03d\n\n- key：%s\n- 字數：%d\n\n%s\n'%(i,key,len(han(src)),src)
p=os.path.join(B,'重作材料_長段','義鈔_句讀待補.md')
io.open(p,'w',encoding='utf-8').write(txt)
print('items',len(items))
