# -*- coding: utf-8 -*-
"""義鈔 25 個 GAP 拆成六批。"""
import io,json,re,os
B=r'C:\Users\lionc\OneDrive\桌面\XW\三大部'; D=os.path.join(B,'測試','重譯','義鈔','_長段','_定稿')
texts={f[:-4]:io.open(os.path.join(D,f),encoding='utf-8').read() for f in os.listdir(D) if f.endswith('.txt')}
def han(s): return ''.join(re.findall(r'[\u4e00-\u9fff]',str(s)))
rows=[json.loads(x) for x in io.open(os.path.join(B,'定稿','yichao.jsonl'),encoding='utf-8') if x.strip()]
items=[]
for r in rows:
 if not r['key'].startswith('GAP'): continue
 th=han(r.get('translation',''))[:20]; hit=''
 for k,t in texts.items():
  if th and th in han(t): hit=k; break
 items.append((r['key'],hit,r.get('source',''),r.get('translation','')))
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
# 刪舊
for f in os.listdir(os.path.join(B,'重作材料_長段')):
 if re.match(r'^義鈔_GAP_長段對應_\d+\.md$',f):
  os.remove(os.path.join(B,'重作材料_長段',f))
n=6; base=len(items)//n; rem=len(items)%n; pos=0
for b in range(n):
 size=base+(1 if b<rem else 0); chunk=items[pos:pos+size]; pos+=size
 if not chunk: continue
 txt=H.format(n=b+1,out='義鈔_GAP_長段對應_%02d_回.md'%(b+1))
 for key,srcfile,src,tr in chunk:
  txt+='\n## %s\n\n- 長段定稿：%s\n\n【原文】\n\n%s\n\n【長段譯文】\n\n%s\n'%(key,srcfile,src,tr)
 fp=os.path.join(B,'重作材料_長段','義鈔_GAP_長段對應_%02d.md'%(b+1))
 io.open(fp,'w',encoding='utf-8').write(txt)
 print(fp,len(chunk),len(txt.encode('utf-8')))
