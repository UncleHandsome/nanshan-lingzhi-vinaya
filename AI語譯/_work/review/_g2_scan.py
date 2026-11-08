import json, io, re
rows=json.load(io.open('AI語譯/_work/review/_g2_rows.json',encoding='utf-8'))
d={ (r['chunk'],r['seg']):r for r in rows }
seen=set()
for l in io.open('AI語譯/_work/review/fix_re2_g2.tsv',encoding='utf-8'):
    f=l.rstrip('\n').split('\t')
    if len(f)!=4: continue
    k=(f[1],f[2])
    if k in seen: continue
    seen.add(k)
    t=f[3]
    sus=[]
    for pat in ['，；','。，','，，','。。','（）','……','；。','、。']:
        if pat in t: sus.append(pat)
    print(f[1],f[2],'len',len(t),'sus',sus)
print('unique segs',len(seen))
