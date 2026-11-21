# -*- coding: utf-8 -*-
"""五書 >500 字長列：不強制字數，要求模型輸出原文／白話起迄標記。"""
import io, json, os, re
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
BOOKS = [('行事鈔','xingshichao'),('戒疏','jieshu'),('業疏','yeshu'),('尼鈔','nicao'),('義鈔','yichao')]
def han(s): return ''.join(re.findall(r'[\u4e00-\u9fff]',str(s)))
items=[]
for name,book in BOOKS:
    rows=[json.loads(x) for x in io.open(os.path.join(B,'定稿',book+'.jsonl'),encoding='utf-8') if x.strip()]
    for r in rows:
        n=len(han(r.get('source','')))
        if n>500:
            items.append((name,r['key'],n,r.get('source',''),r.get('translation','')))
H='''# 五書長段切分（>500 字，第 {batch} 批）

## 輸出檔名
```text
{out}
```

## 任務
依文意把每一列切成小段：問答、科判、段落、引文起訖。
**不要固定 300–500 字，也不要整列不切。**

## 輸出格式
每小段只輸出起迄標記，不要重抄全文：

```text
## L001-1
原文起：<原文開頭 10–15 字>
原文迄：<原文結尾 10–15 字>
白話起：<白話開頭 10–15 字>
白話迄：<白話結尾 10–15 字>
```

## 規則
- 起迄文字必須在該列原文／白話中可唯一定位
- 各段依序、不重疊、不漏字
- 原文起迄與白話起迄要對應同一段
- 不改字、不增刪、不翻譯

---
'''
LIMIT=200*1024
# 刪舊檔
for f in os.listdir(os.path.join(B,'重作材料_長段')):
    if re.match(r'^長段待切500_\d+\.md$',f):
        os.remove(os.path.join(B,'重作材料_長段',f))
batches=[];cur=[];size=0
for i,(name,key,n,src,tr) in enumerate(items,1):
    block='\n## L%03d\n\n- 書：%s\n- key：%s\n- 字數：%d\n\n【原文】\n\n%s\n\n【現譯】\n\n%s\n'%(i,name,key,n,src,tr)
    b=len(block.encode('utf-8'))
    if cur and size+b>LIMIT:
        batches.append(cur);cur=[];size=0
    cur.append(block);size+=b
if cur:batches.append(cur)
for b,blocks in enumerate(batches,1):
    txt=H.format(batch=b,out='長段待切500_%02d_回.md'%b)+''.join(blocks)
    fp=os.path.join(B,'重作材料_長段','長段待切500_%02d.md'%b)
    io.open(fp,'w',encoding='utf-8').write(txt)
    print(fp,len(blocks),len(txt.encode('utf-8')))
print('total',len(items),'batches',len(batches))
