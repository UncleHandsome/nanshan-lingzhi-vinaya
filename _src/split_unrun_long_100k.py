# -*- coding: utf-8 -*-
"""把長段未跑材料改成每批約 100KB。"""
import io,json,re,os
B=r'C:\Users\lionc\OneDrive\桌面\XW\三大部'; S=os.path.join(B,'重作材料_長段')
def han(s): return ''.join(re.findall(r'[\u4e00-\u9fff]',str(s)))
BOOKS=[('行事鈔','xingshichao'),('戒疏','jieshu'),('業疏','yeshu'),('尼鈔','nicao'),('義鈔','yichao')]
items=[]
for name,book in BOOKS:
 rows=[json.loads(x) for x in io.open(os.path.join(B,'定稿',book+'.jsonl'),encoding='utf-8') if x.strip()]
 for r in rows:
  if len(han(r.get('source','')))>500:
   items.append((name,r['key'],len(han(r['source'])),r['source'],r.get('translation','')))
done=set(re.findall(r'^## L(\d+)-',io.open(os.path.join(S,'long.txt'),encoding='utf-8').read(),re.M))
miss=[(i,x) for i,x in enumerate(items,1) if '%03d'%i not in done]
for f in os.listdir(S):
 if re.match(r'^長段_未跑_\d+\.md$',f): os.remove(os.path.join(S,f))
H='''# 五書長段切分（未跑，第 {n} 批）

## 輸出檔名
```text
長段_未跑_回_{n}.md
```

## 任務
依文意把每一列切成小段：問答、科判、段落、引文起訖。

## 輸出格式
```text
## L001-1
原文起：<原文開頭 10–15 字>
原文迄：<原文結尾 10–15 字>
白話起：<白話開頭 10–15 字>
白話迄：<白話結尾 10–15 字>
```
- 起迄要能唯一定位
- 依序、不重疊、不漏
- 不改字、不增刪

---
'''
LIMIT=100*1024; batches=[];cur=[];size=0
for num,(name,key,n,src,tr) in miss:
 block='\n## L%03d\n\n- 書：%s\n- key：%s\n- 字數：%d\n\n【原文】\n\n%s\n\n【現譯】\n\n%s\n'%(num,name,key,n,src,tr)
 b=len(block.encode('utf-8'))
 if cur and size+b>LIMIT: batches.append(cur);cur=[];size=0
 cur.append(block);size+=b
if cur:batches.append(cur)
for i,blocks in enumerate(batches,1):
 txt=H.format(n=i)+''.join(blocks)
 p=os.path.join(S,'長段_未跑_%02d.md'%i)
 io.open(p,'w',encoding='utf-8').write(txt)
 print(p,len(blocks),len(txt.encode('utf-8')))
print('items',len(miss),'batches',len(batches))
