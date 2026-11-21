# -*- coding: utf-8 -*-
"""套用業疏補句讀回覆：只寫 display_source，漢字必須完全一致。"""
import io, json, os, re
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
def han(s): return ''.join(re.findall(r'[\u4e00-\u9fff]', str(s)))
rp=os.path.join(B,'重作材料_長段','業疏_句讀補漏_回.md')
if not os.path.exists(rp):
    raise SystemExit('尚未產生：'+rp)
t=io.open(rp,encoding='utf-8').read()
parts=[]
for m in re.finditer(r'## 業疏-P(\d+)\s*\n(.*?)(?=^## |\Z)',t,re.M|re.S):
    body=m.group(2).strip()
    body=re.sub(r'^```[a-z]*\s*|\s*```$','',body).strip()
    parts.append(body)
p=os.path.join(B,'定稿','yeshu.jsonl')
rows=[json.loads(x) for x in io.open(p,encoding='utf-8') if x.strip()]
used=set(); hit=0; miss=[]
for body in parts:
    bh=han(body)
    if not bh: continue
    for r in rows:
        for s in r.get('segments') or []:
            if id(s) in used: continue
            if han(s.get('source',''))==bh:
                s['display_source']=body; used.add(id(s)); hit+=1; break
        else:
            continue
        break
    else:
        miss.append(bh[:40])
io.open(p,'w',encoding='utf-8').writelines(json.dumps(r,ensure_ascii=False)+'\n' for r in rows)
print('parts',len(parts),'hit',hit,'miss',len(miss))
for x in miss[:10]: print('MISS',x)
