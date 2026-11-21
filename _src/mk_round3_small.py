# -*- coding: utf-8 -*-
"""第四輪：long3/gap3 崩潰後，改成更小包。"""
import io,json,re,os
B=r'C:\Users\lionc\OneDrive\桌面\XW\三大部'; S=os.path.join(B,'重作材料_長段')
def rd(f): return io.open(os.path.join(S,f),encoding='utf-8').read()
def han(s): return ''.join(re.findall(r'[\u4e00-\u9fff]',str(s)))

BOOKS=[('行事鈔','xingshichao'),('戒疏','jieshu'),('業疏','yeshu'),('尼鈔','nicao'),('義鈔','yichao')]
items=[]
for name,book in BOOKS:
    rows=[json.loads(x) for x in io.open(os.path.join(B,'定稿',book+'.jsonl'),encoding='utf-8') if x.strip()]
    for r in rows:
        if len(han(r.get('source','')))>500:
            items.append((name,r['key'],len(han(r['source'])),r['source'],r.get('translation','')))
done=set()
for f in ('long.txt','long2.txt','long3.txt'):
    done|=set(re.findall(r'^## L(\d+)-',rd(f),re.M))
miss=[(i,x) for i,x in enumerate(items,1) if '%03d'%i not in done]
print('long miss',len(miss))
H='''# 五書長段切分（第 {n} 包）

## 輸出檔名
```text
長段_未跑3_回_{n}.md
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
LIMIT=25*1024; MAXITEMS=3
batches=[];cur=[];size=0
for num,(name,key,n,src,tr) in miss:
    block='\n## L%03d\n\n- 書：%s\n- key：%s\n- 字數：%d\n\n【原文】\n\n%s\n\n【現譯】\n\n%s\n'%(num,name,key,n,src,tr)
    b=len(block.encode('utf-8'))
    if cur and (size+b>LIMIT or len(cur)>=MAXITEMS):
        batches.append(cur);cur=[];size=0
    cur.append(block);size+=b
if cur:batches.append(cur)
for i,blocks in enumerate(batches,1):
    p=os.path.join(S,'長段_未跑3_%02d.md'%i)
    io.open(p,'w',encoding='utf-8').write(H.format(n=i)+''.join(blocks))
    print(p,len(blocks),os.path.getsize(p))
print('long batches',len(batches))

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
doneg=set()
for f in ('GAP.txt','gap2.txt','gap3.txt'):
    doneg|=set(re.findall(r'^## (GAP\d+)-\d+',rd(f),re.M))
missg=[x for x in gitems if x[0] not in doneg]
print('gap miss',[x[0] for x in missg])
G='''# 義鈔 GAP 長段對應（第 {n} 包）

## 輸出檔名
```text
義鈔GAP_未跑3_回_{n}.md
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
for i,(key,srcfile,src,tr) in enumerate(missg,1):
    block='\n## %s\n\n- 長段定稿：%s\n\n【原文】\n\n%s\n\n【長段譯文】\n\n%s\n'%(key,srcfile,src,tr)
    p=os.path.join(S,'義鈔GAP_未跑3_%02d.md'%i)
    io.open(p,'w',encoding='utf-8').write(G.format(n=i)+block)
    print(p,os.path.getsize(p))
