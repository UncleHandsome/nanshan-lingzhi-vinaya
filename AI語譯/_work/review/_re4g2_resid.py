# -*- coding: utf-8 -*-
import json, re
rows = json.load(open(r'AI語譯/_work/review/_re4g2_rows.json', encoding='utf-8'))
outs = json.load(open(r'AI語譯/_work/review/_re4g2_out_rows.json', encoding='utf-8'))
bykey = {}
for d in rows:
    bykey.setdefault((d['book'], d['chunk'], d['seg']), []).append(d)
newmap = {(b, c, s): t for b, c, s, t in outs}
f = open(r'AI語譯/_work/review/_re4g2_residual.txt', 'w', encoding='utf-8')
cnt = 0
for key, ds in bykey.items():
    new = newmap.get(key)
    if new is None:
        continue
    for d in ds:
        cur = d['current']
        qs = [x for x in re.findall(r'[「『](.*?)[」』]', d['problem']) if len(x) >= 8]
        for q in qs:
            if q in cur and q in new:
                cnt += 1
                f.write("%d %s seg=%s still-quoted: %s\n" % (d['_n'], d['chunk'], d['seg'], q[:60]))
f.close()
print('residual', cnt)
