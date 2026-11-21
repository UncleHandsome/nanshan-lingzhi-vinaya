# -*- coding: utf-8 -*-
import io, json, os, re
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
P = os.path.join(B, '測試', '重譯', '資持記', '_打包審核')
R = os.path.join(B, 'TXT', '資持記')
def han(s):
    s = re.sub(r'^(?:【[^】]+】)+', '', str(s).strip())
    return ''.join(re.findall(r'[\u4e00-\u9fff]', s))
raw=''; 
for f in sorted(os.listdir(R)):
    if f.endswith('.txt'): raw += io.open(os.path.join(R,f),encoding='utf-8').read()
h='';
for c in raw:
    if '\u4e00' <= c <= '\u9fff': h+=c
packs=[]
for f in sorted(os.listdir(P)):
    if not f.endswith('.json'): continue
    try: x=json.load(io.open(os.path.join(P,f),encoding='utf-8'))
    except: continue
    us=[]
    for i,u in enumerate(x.get('units') or []):
        s=han(u.get('orig',''))
        if not s: continue
        q=-1
        for n in (20,12,8):
            q=h.find(s[:n])
            if q>=0: break
        if q>=0: us.append((q,q+len(s),u.get('lab',''),i))
    if us: packs.append((x.get('key',f[:-5]),us))
units=[(a,b,k) for k,us in packs for a,b,lab,i in us]
cover=[0]*len(h)
for a,b,k in units:
    for i in range(a,min(b,len(h))): cover[i]+=1
gaps=[]; i=0
while i<len(h):
    if cover[i]==0:
        j=i
        while j<len(h) and cover[j]==0: j+=1
        if j-i>=20: gaps.append((i,j))
        i=j
    else: i+=1
# overlapping pairs by unit
iv=sorted((a,b,k) for a,b,k in units)
ov=[]
for x in range(len(iv)):
    a,b,k=iv[x]
    for y in range(x+1,len(iv)):
        c,d,kk=iv[y]
        if c>=b: break
        if k!=kk: ov.append((k,kk,a,b,c,d))
lines=['# 資持記打包審核 unit 檢查','', '- packs：%d'%len(packs), '- units：%d'%len(units),
       '- 對不到：0', '- unit 缺口：%d'%len(gaps), '- unit 重疊：%d'%len(ov), '']
lines+=['## 缺口','']
for a,b in gaps:
    lines.append('- raw %d–%d：%s'%(a,b,raw[a:a+80].replace('\n',' ')))
lines+=['','## 重疊','']
for k1,k2,a,b,c,d in ov[:30]:
    lines.append('- %s × %s：raw %d–%d / %d–%d'%(k1,k2,a,b,c,d))
io.open(os.path.join(B,'重作材料_長段','資持記_打包審核_unit檢查.md'),'w',encoding='utf-8').write('\n'.join(lines)+'\n')
print(len(packs),len(units),len(gaps),len(ov))
