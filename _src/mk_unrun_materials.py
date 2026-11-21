# -*- coding: utf-8 -*-
"""依 long.txt / judge.txt / GAP.txt 已回覆的編號，產出還沒跑的 materials。"""
import io,json,re,os
B=r'C:\Users\lionc\OneDrive\桌面\XW\三大部'; S=os.path.join(B,'重作材料_長段')
def txt(f): return io.open(os.path.join(S,f),encoding='utf-8').read()
def han(s): return ''.join(re.findall(r'[\u4e00-\u9fff]',str(s)))

# 長段：全部 119 列
BOOKS=[('行事鈔','xingshichao'),('戒疏','jieshu'),('業疏','yeshu'),('尼鈔','nicao'),('義鈔','yichao')]
long_items=[]
for name,book in BOOKS:
    rows=[json.loads(x) for x in io.open(os.path.join(B,'定稿',book+'.jsonl'),encoding='utf-8') if x.strip()]
    for r in rows:
        if len(han(r.get('source','')))>500:
            long_items.append((name,r['key'],len(han(r['source'])),r['source'],r.get('translation','')))
done=set(re.findall(r'^## L(\d+)-',txt('long.txt'),re.M))
miss=[(i,x) for i,x in enumerate(long_items,1) if '%03d'%i not in done]
print('long total',len(long_items),'done',len(done),'miss',len(miss))
H='''# 五書長段切分（未跑）

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
LIMIT=200*1024; batches=[];cur=[];size=0
for num,(name,key,n,src,tr) in miss:
    block='\n## L%03d\n\n- 書：%s\n- key：%s\n- 字數：%d\n\n【原文】\n\n%s\n\n【現譯】\n\n%s\n'%(num,name,key,n,src,tr)
    b=len(block.encode('utf-8'))
    if cur and size+b>LIMIT: batches.append(cur);cur=[];size=0
    cur.append(block);size+=b
if cur:batches.append(cur)
for i,blocks in enumerate(batches,1):
    p=os.path.join(S,'長段_未跑_%02d.md'%i)
    io.open(p,'w',encoding='utf-8').write(H.format(n=i)+''.join(blocks))
    print(p,len(blocks),len(io.open(p,encoding='utf-8').read().encode('utf-8')))

# 裁決：19 key 中未回
judge_all=io.open(os.path.join(S,'資持記_裁決失敗19_keys.txt'),encoding='utf-8').read().split()
jdone=set(re.findall(r'^## KEY (\S+)',txt('judge.txt'),re.M))
jmiss=[k for k in judge_all if k not in jdone]
print('judge miss',jmiss)
if jmiss:
    J='''# 資持記 裁決重跑（未跑）

## 輸出檔名
```text
裁決_未跑_回.md
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
PASS_A 要寫 `PASS_A_KEEP_A`；REVISED 要完整譯文；不改原文。

---
'''
    for k in jmiss:
        J+='\n## KEY %s\n\n%s\n\n---\n'%(k,io.open(os.path.join(B,'測試','重譯','資持記','_裁決_重跑',k+'.md'),encoding='utf-8').read())
    io.open(os.path.join(S,'裁決_未跑_材料.md'),'w',encoding='utf-8').write(J)

# GAP：25 個中未回
D=os.path.join(B,'測試','重譯','義鈔','_長段','_定稿')
texts={f[:-4]:io.open(os.path.join(D,f),encoding='utf-8').read() for f in os.listdir(D) if f.endswith('.txt')}
rows=[json.loads(x) for x in io.open(os.path.join(B,'定稿','yichao.jsonl'),encoding='utf-8') if x.strip()]
gitems=[]
for r in rows:
    if not r['key'].startswith('GAP'): continue
    th=han(r.get('translation',''))[:20]; hit=''
    for k,t in texts.items():
        if th and th in han(t): hit=k;break
    gitems.append((r['key'],hit,r['source'],r.get('translation','')))
gdone=set(re.findall(r'^## (GAP\d+)-\d+',txt('GAP.txt'),re.M))
gmiss=[x for x in gitems if x[0] not in gdone]
print('gap miss',len(gmiss),[x[0] for x in gmiss])
if gmiss:
    G='''# 義鈔 GAP 長段對應（未跑）

## 輸出檔名
```text
義鈔GAP_未跑_回.md
```

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
    for key,srcfile,src,tr in gmiss:
        G+='\n## %s\n\n- 長段定稿：%s\n\n【原文】\n\n%s\n\n【長段譯文】\n\n%s\n'%(key,srcfile,src,tr)
    io.open(os.path.join(S,'義鈔GAP_未跑_材料.md'),'w',encoding='utf-8').write(G)
