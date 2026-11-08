import json, io
rows=json.load(io.open('AI語譯/_work/review/_g2_rows.json',encoding='utf-8'))
cur={(r['chunk'],r['seg']):r['current'] for r in rows}
books=set(); n=0; same=0
for l in io.open('AI語譯/_work/review/fix_re2_g2.tsv',encoding='utf-8'):
    f=l.rstrip('\n').split('\t')
    if len(f)!=4: continue
    n+=1; books.add(f[0])
    if cur.get((f[1],f[2]))==f[3]: same+=1
print('rows',n,'books',books,'unchanged',same)
print('bom?', open('AI語譯/_work/review/fix_re2_g2.tsv','rb').read(3))
