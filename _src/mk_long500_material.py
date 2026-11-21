# -*- coding: utf-8 -*-
"""五書 >500 字長列，切三批材料。"""
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
H='''# 五書長段待切（>500 字，第 {batch} 批）

## 輸出檔名
```text
{out}
```

## 任務
把每一列切成 300–500 字的小段，原文與白話一起切，不可只切原文。

- 保留所有字，順序不變
- 每小段輸出：
```text
## L編號-1
【原文】
……
【白話】
……
```
- 原文與白話切點要對應
- 不改字、不增刪、不翻譯

---
'''
for b in range(3):
    chunk=items[b*40:(b+1)*40]
    txt=H.format(batch=b+1,out='長段待切500_%02d_回.md'%(b+1))
    for i,(name,key,n,src,tr) in enumerate(chunk,b*40+1):
        txt+='\n## L%03d\n\n- 書：%s\n- key：%s\n- 字數：%d\n\n【原文】\n\n%s\n\n【現譯】\n\n%s\n'%(i,name,key,n,src,tr)
    fp=os.path.join(B,'重作材料_長段','長段待切500_%02d.md'%(b+1))
    io.open(fp,'w',encoding='utf-8').write(txt)
    print(fp,len(chunk))
print('total',len(items))
