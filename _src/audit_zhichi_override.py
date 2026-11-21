import io, json, os, re
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
P = os.path.join(B, '測試', '重譯', '資持記', '_打包審核')
R = os.path.join(B, 'TXT', '資持記')
OV = json.load(io.open(os.path.join(B, '重作材料_長段', '資持記_unit_override.json'), encoding='utf-8'))
def han(s):
    s = re.sub(r'^(?:【[^】]+】)+', '', str(s).strip())
    return ''.join(re.findall(r'[\u4e00-\u9fff]', s))
raw=''
for f in sorted(os.listdir(R)):
    if f.endswith('.txt'): raw += io.open(os.path.join(R,f),encoding='utf-8').read()
h=''
for c in raw:
    if '\u4e00'<=c<='\u9fff': h+=c
units=[]
for f in sorted(os.listdir(P)):
    if not f.endswith('.json'): continue
    try: x=json.load(io.open(os.path.join(P,f),encoding='utf-8'))
    except: continue
    k=x.get('key',f[:-5])
    for i,u in enumerate(x.get('units') or []):
        s=han(u.get('orig',''))
        if not s: continue
        ov=OV.get('%s|%d'%(k,i))
        if ov:
            a,b=ov['raw_start'],ov['raw_end']
        else:
            q=-1
            for n in (20,12,8):
                q=h.find(s[:n])
                if q>=0: break
            if q<0: continue
            a,b=q,q+len(s)
        units.append((a,b,k))
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
dups=sum(1 for a,b,k in units if any(cover[i]>1 for i in range(a,min(b,len(h)))))
print('units',len(units),'gaps',len(gaps),'overlaps',dups)
