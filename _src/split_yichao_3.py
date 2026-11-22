# -*- coding: utf-8 -*-
"""把過長的義鈔 GAP06/13/14 切成小包材料。"""
import io,json,re,os,shutil
B=r'C:\Users\lionc\OneDrive\桌面\XW\三大部'; rows=[json.loads(x) for x in io.open(os.path.join(B,'定稿','yichao.jsonl'),encoding='utf-8') if x.strip()]
def han(s): return ''.join(re.findall(r'[\u4e00-\u9fff]',str(s)))
def split_at(s,n):
    if n<=1: return [s]
    target=len(s)//n; cuts=[0]
    for k in range(1,n):
        lo=cuts[-1]+max(1,target//2); hi=min(len(s)-1,cuts[-1]+target*3//2)
        pos=-1
        for p in range(hi,lo,-1):
            if s[p] in '。！？；':
                pos=p+1;break
        if pos<0: pos=min(len(s)-1,cuts[-1]+target)
        cuts.append(pos)
    cuts.append(len(s))
    return [s[cuts[i]:cuts[i+1]] for i in range(len(cuts)-1)]
out=os.path.join(B,'重作材料_長段','義鈔_長段_小包')
if os.path.isdir(out): shutil.rmtree(out)
os.makedirs(out)
H='''你是古籍整理員。請依文意把下面這一段切成小段，原文與白話都要切。

## 輸出格式
```text
## {key}-1
原文起：<原文開頭 10–15 字>
原文迄：<原文結尾 10–15 字>
白話起：<白話開頭 10–15 字>
白話迄：<白話結尾 10–15 字>
```
- 起迄要能唯一定位
- 依序、不重疊、不漏
- 白話起迄必須從【現譯】擷取
- 不可寫「（現譯從缺）」
- 不改字、不增刪、不翻譯

---

【原文】

{src}

【現譯】

{tr}
'''
count=0
for key,n in [('GAP06',3),('GAP13',5),('GAP14',4)]:
    r=next((r for r in rows if r['key']==key),None)
    if not r: continue
    ss=split_at(r['source'],n); tt=split_at(r.get('translation',''),n)
    # 對齊段數：以原文段數為主
    for i in range(n):
        s=ss[i] if i<len(ss) else ''
        t=tt[i] if i<len(tt) else ''
        if not s or not t: continue
        k='%s_%02d'%(key,i+1)
        p=os.path.join(out,'義鈔_%s.md'%k)
        io.open(p,'w',encoding='utf-8').write(H.format(key=k,src=s,tr=t)); count+=1
print('files',count)