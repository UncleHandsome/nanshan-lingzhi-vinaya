import json, io
rows=json.load(io.open('AI語譯/_work/review/_g2_rows.json',encoding='utf-8'))
out={}
for l in io.open('AI語譯/_work/review/fix_re2_g2.tsv',encoding='utf-8'):
    f=l.rstrip('\n').split('\t')
    if len(f)==4: out.setdefault((f[1],f[2]),[]).append(f[3])
d={r['idx']:r for r in rows}
for idx in [3]:
    print('=== idx',idx,'len',len(out[(d[idx]['chunk'],d[idx]['seg'])][0]))
    print(out[(d[idx]['chunk'],d[idx]['seg'])][0])
print()
for idx,phr in [(1,'僧法軌度'),(7,'結夏安居'),(8,'三種條例'),(10,'迦提利法'),(18,'白告暫停'),(22,'上下篇互望'),(26,'是出自《摩訶僧祇律》'),(33,'四種心'),(41,'戒本之外'),(43,'奪回'),(44,'長食'),(45,'上房'),(46,'比丘犯重罪'),(48,'守護者自己'),(53,'今正判定'),(58,'食器分發'),(59,'溺死'),(64,'第二天沒有獲得'),(65,'古德解釋'),(71,'惡剎利')]:
    t=out[(d[idx]['chunk'],d[idx]['seg'])][0]
    i=t.find(phr)
    print('---',idx,phr,'at',i)
    print(t[max(0,i-90):i+160] if i>=0 else 'NOT FOUND')
