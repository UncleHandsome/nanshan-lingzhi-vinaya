# -*- coding: utf-8 -*-
import io,os,math
B=r'C:\Users\lionc\OneDrive\桌面\XW\三大部'; d=os.path.join(B,'測試','重譯','資持記','_裁決_重跑')
keys=io.open(os.path.join(B,'重作材料_長段','資持記_裁決失敗19_keys.txt'),encoding='utf-8').read().split()
H='''# 資持記 裁決重跑材料（第 {n} 批）

## 輸出檔名
```text
{out}
```

## 任務
下面每一份是一個 key 的裁決材料。逐份重新裁決，不要把研究筆記當答案。

每份輸出必須有：
```text
## KEY <key>
【結論】
PASS_A 或 REVISED

【分歧與裁決】
……

【修正後的譯文】
……
```
- PASS_A 也要寫 `PASS_A_KEEP_A`
- REVISED 必須完整給修正後譯文
- 不改原文

---

'''
n_batches=4
size=math.ceil(len(keys)/n_batches)
for n in range(n_batches):
    ch=keys[n*size:(n+1)*size]
    if not ch: continue
    txt=H.format(n=n+1,out='資持記_裁決重跑_材料_%02d_回.md'%(n+1))
    for k in ch:
        body=io.open(os.path.join(d,k+'.md'),encoding='utf-8').read()
        txt+='\n## KEY %s\n\n%s\n\n---\n'%(k,body)
    fp=os.path.join(B,'重作材料_長段','資持記_裁決重跑_材料_%02d.md'%(n+1))
    io.open(fp,'w',encoding='utf-8').write(txt)
    print(fp,len(ch),len(txt.encode('utf-8')))
# 刪舊的 02（若存在且不是新四批之一）
for f in ['資持記_裁決重跑_材料_02.md']:
    p=os.path.join(B,'重作材料_長段',f)
    if os.path.exists(p) and n_batches<3: os.remove(p)
