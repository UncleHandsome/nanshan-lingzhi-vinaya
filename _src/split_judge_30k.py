# -*- coding: utf-8 -*-
"""裁決重跑 19 key 材料，每批約 30KB。"""
import io,os,re
B=r'C:\Users\lionc\OneDrive\桌面\XW\三大部'; S=os.path.join(B,'重作材料_長段'); d=os.path.join(B,'測試','重譯','資持記','_裁決_重跑')
keys=io.open(os.path.join(S,'資持記_裁決失敗19_keys.txt'),encoding='utf-8').read().split()
H='''# 資持記 裁決重跑材料（第 {n} 批）

## 輸出檔名
```text
{out}
```

## 任務
逐份重新裁決，不要把研究筆記當答案。

每份輸出：
```text
## KEY <key>
【結論】
PASS_A 或 REVISED

【分歧與裁決】
……

【修正後的譯文】
……
```
- PASS_A 要寫 `PASS_A_KEEP_A`
- REVISED 要完整譯文
- 不改原文

---

'''
for f in os.listdir(S):
    if re.match(r'^資持記_裁決重跑_材料_\d+\.md$',f): os.remove(os.path.join(S,f))
LIMIT=30*1024; batches=[];cur=[];size=0
for k in keys:
    block='\n## KEY %s\n\n%s\n\n---\n'%(k,io.open(os.path.join(d,k+'.md'),encoding='utf-8').read())
    b=len(block.encode('utf-8'))
    if cur and size+b>LIMIT: batches.append(cur);cur=[];size=0
    cur.append(block);size+=b
if cur:batches.append(cur)
for i,blocks in enumerate(batches,1):
    txt=H.format(n=i,out='資持記_裁決重跑_材料_%02d_回.md'%i)+''.join(blocks)
    p=os.path.join(S,'資持記_裁決重跑_材料_%02d.md'%i)
    io.open(p,'w',encoding='utf-8').write(txt)
    print(p,len(blocks),len(txt.encode('utf-8')))
print('batches',len(batches))
