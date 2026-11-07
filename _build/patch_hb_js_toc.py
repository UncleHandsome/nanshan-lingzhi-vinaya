import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\hebian_ju.py'
s = io.open(p, encoding='utf-8').read()

# 1) flat 帶上分塊 key
old = """for k,sp,tt in cs:
    vol=k.split('_',1)[1] if '_' in k else k
    if vol.startswith('卷首'):
        vol='卷上之一'      # 卷首併入第一卷
    if vol not in vols: vols.append(vol)
    for i in range(len(sp)):
        flat.append((sp[i], tt[i] if i < len(tt) else '', vol))"""
new = """for k,sp,tt in cs:
    vol=k.split('_',1)[1] if '_' in k else k
    if vol.startswith('卷首'):
        vol='卷上之一'      # 卷首併入第一卷
    if vol not in vols: vols.append(vol)
    for i in range(len(sp)):
        flat.append((sp[i], tt[i] if i < len(tt) else '', vol, k))"""
if old in s:
    s = s.replace(old, new)

# 2) 解析：卷首的篇名目次不建立 section
old2 = """PRE=[]          # 卷首（篇1 之前的鈔文）
for o,t,vol in flat:
    if cur is None and vol=='卷上之一':
        PRE.append((o,t,vol))
    m=PATS.match(o)
    if m:"""
new2 = """PRE=[]          # 卷首（篇1 之前的鈔文）
for o,t,vol,key in flat:
    in_js = key.startswith('00_')
    if in_js:
        if PATS.match(o) or PATS2.match(o):
            continue          # 卷首目次，不當篇名
        PRE.append((o,t,vol))
        continue
    m=PATS.match(o)
    if m:"""
if old2 in s:
    s = s.replace(old2, new2)

# 3) 迴圈變數修正（後面用到 vol）
s = s.replace("    for i in range(len(sp)):\n        flat.append((sp[i], tt[i] if i < len(tt) else '', vol, k))",
              "    for i in range(len(sp)):\n        flat.append((sp[i], tt[i] if i < len(tt) else '', vol, k))")

# 4) build 內 idxs 仍用 sec['items'] 三元組，補回
s = s.replace("idxs=[i for i,(o,t,v) in enumerate(sec['items']) if v==vol and not SKIP1.match(o.strip()) and not SKIP2.match(o.strip())]",
              "idxs=[i for i,(o,t,v,*_) in enumerate(sec['items']) if v==vol and not SKIP1.match(o.strip()) and not SKIP2.match(o.strip())]")
s = s.replace("first_all = min([i for i, (o, t, v) in enumerate(sec['items'])",
              "first_all = min([i for i, (o, t, v, *_) in enumerate(sec['items'])")
io.open(p, 'w', encoding='utf-8').write(s)
print('hebian_ju 卷首目次 patched')
