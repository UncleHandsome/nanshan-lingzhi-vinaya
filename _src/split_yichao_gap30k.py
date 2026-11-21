# -*- coding: utf-8 -*-
"""義鈔 25 個 GAP 材料，每批約 30KB。"""
import io,json,re,os
B=r'C:\Users\lionc\OneDrive\桌面\XW\三大部'; S=os.path.join(B,'重作材料_長段'); D=os.path.join(B,'測試','重譯','義鈔','_長段','_定稿')
texts={f[:-4]:io.open(os.path.join(D,f),encoding='utf-8').read() for f in os.listdir(D) if f.endswith('.txt')}
def han(s): return ''.join(re.findall(r'[\u4e00-\u9fff]',str(s)))
rows=[json.loads(x) for x in io.open(os.path.join(B,'定稿','yichao.jsonl'),encoding='utf-8') if x.strip()]
items=[]
for r in rows:
 if not r['key'].startswith('GAP'): continue
 th=han(r.get('translation',''))[:20]; hit=''
 for k,t in texts.items():
  if th and th in han(t): hit=k;break
 items.append((r['key'],hit,r['source'],r.get('translation','')))
H='''# 義鈔 GAP 長段對應（第 {n} 批）

## 輸出檔名
```text
{out}
```

## 任務
每個 GAP 都已從 `_長段/_定稿` 找到對應譯文。
請把原文與長段譯文切成互相對應的小段。

## 格式
```text
## GAP01-1
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
for f in os.listdir(S):
 if re.match(r'^義鈔_GAP_長段對應_\d+\.md$',f): os.remove(os.path.join(S,f))
LIMIT=30*1024; batches=[];cur=[];size=0
for key,srcfile,src,tr in items:
 block='\n## %s\n\n- 長段定稿：%s\n\n【原文】\n\n%s\n\n【長段譯文】\n\n%s\n'%(key,srcfile,src,tr)
 b=len(block.encode('utf-8'))
 if cur and size+b>LIMIT: batches.append(cur);cur=[];size=0
 cur.append(block);size+=b
if cur:batches.append(cur)
for i,blocks in enumerate(batches,1):
 txt=H.format(n=i,out='義鈔_GAP_長段對應_%02d_回.md'%i)+''.join(blocks)
 p=os.path.join(S,'義鈔_GAP_長段對應_%02d.md'%i)
 io.open(p,'w',encoding='utf-8').write(txt)
 print(p,len(blocks),len(txt.encode('utf-8')))
print('batches',len(batches))
