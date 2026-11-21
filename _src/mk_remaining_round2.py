# -*- coding: utf-8 -*-
"""第三輪：只產還沒回覆的材料，套件大小再減半。"""
import io,json,re,os
B=r'C:\Users\lionc\OneDrive\桌面\XW\三大部'; S=os.path.join(B,'重作材料_長段')
def rd(f): return io.open(os.path.join(S,f),encoding='utf-8').read()
def han(s): return ''.join(re.findall(r'[\u4e00-\u9fff]',str(s)))

# 長段
BOOKS=[('行事鈔','xingshichao'),('戒疏','jieshu'),('業疏','yeshu'),('尼鈔','nicao'),('義鈔','yichao')]
items=[]
for name,book in BOOKS:
    rows=[json.loads(x) for x in io.open(os.path.join(B,'定稿',book+'.jsonl'),encoding='utf-8') if x.strip()]
    for r in rows:
        if len(han(r.get('source','')))>500:
            items.append((name,r['key'],len(han(r['source'])),r['source'],r.get('translation','')))
done=set(re.findall(r'^## L(\d+)-',rd('long.txt'),re.M))|set(re.findall(r'^## L(\d+)-',rd('long2.txt'),re.M))
miss=[(i,x) for i,x in enumerate(items,1) if '%03d'%i not in done]
H='''# 五書長段切分（未跑，第 {n} 包）

## 輸出檔名
```text
長段_未跑2_回_{n}.md
```

## 任務
依文意把每一列切成小段：問答、科判、段落、引文起訖。

## 格式
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
LIMIT=50*1024; batches=[];cur=[];size=0
for num,(name,key,n,src,tr) in miss:
    block='\n## L%03d\n\n- 書：%s\n- key：%s\n- 字數：%d\n\n【原文】\n\n%s\n\n【現譯】\n\n%s\n'%(num,name,key,n,src,tr)
    b=len(block.encode('utf-8'))
    if cur and size+b>LIMIT: batches.append(cur);cur=[];size=0
    cur.append(block);size+=b
if cur:batches.append(cur)
for i,blocks in enumerate(batches,1):
    p=os.path.join(S,'長段_未跑2_%02d.md'%i)
    io.open(p,'w',encoding='utf-8').write(H.format(n=i)+''.join(blocks))
    print(p,len(blocks),os.path.getsize(p))
print('long miss',len(miss),'batches',len(batches))

# 裁決
allj=io.open(os.path.join(S,'資持記_裁決失敗19_keys.txt'),encoding='utf-8').read().split()
donej=set(re.findall(r'^## KEY (\S+)',rd('judge.txt'),re.M))|set(re.findall(r'^## KEY (\S+)',rd('judge2.txt'),re.M))
missj=[k for k in allj if k not in donej]
print('judge miss',missj)
if missj:
    J='''# 資持記 裁決重跑（未跑）

## 輸出檔名
```text
裁決_未跑2_回.md
```

只裁決以下 key；格式同之前。

---
'''
    for k in missj:
        J+='\n## KEY %s\n\n%s\n\n---\n'%(k,io.open(os.path.join(B,'測試','重譯','資持記','_裁決_重跑',k+'.md'),encoding='utf-8').read())
    io.open(os.path.join(S,'裁決_未跑2_材料.md'),'w',encoding='utf-8').write(J)

# GAP
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
doneg=set(re.findall(r'^## (GAP\d+)-\d+',rd('GAP.txt'),re.M))|set(re.findall(r'^## (GAP\d+)-\d+',rd('gap2.txt'),re.M))
missg=[x for x in gitems if x[0] not in doneg]
print('gap miss',[x[0] for x in missg])
if missg:
    G='''# 義鈔 GAP 長段對應（未跑）

## 輸出檔名
```text
義鈔GAP_未跑2_回_{n}.md
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
    LIMIT=15*1024; batches=[];cur=[];size=0
    for key,srcfile,src,tr in missg:
        block='\n## %s\n\n- 長段定稿：%s\n\n【原文】\n\n%s\n\n【長段譯文】\n\n%s\n'%(key,srcfile,src,tr)
        b=len(block.encode('utf-8'))
        if cur and size+b>LIMIT: batches.append(cur);cur=[];size=0
        cur.append(block);size+=b
    if cur:batches.append(cur)
    for i,blocks in enumerate(batches,1):
        p=os.path.join(S,'義鈔GAP_未跑2_%02d.md'%i)
        io.open(p,'w',encoding='utf-8').write(G.format(n=i)+''.join(blocks))
        print(p,len(blocks),os.path.getsize(p))
