# -*- coding: utf-8 -*-
import json
from collections import Counter, defaultdict
outs = json.load(open(r'AI語譯/_work/review/_re4g2_out_rows.json', encoding='utf-8'))
cnt = Counter((b, c, s) for b, c, s, _ in outs)
dups = {k: v for k, v in cnt.items() if v > 1}
print('dup keys:', len(dups))
rows = json.load(open(r'AI語譯/_work/review/_re4g2_rows.json', encoding='utf-8'))
bykey = defaultdict(list)
for d in rows:
    bykey[(d['book'], d['chunk'], d['seg'])].append(d['_n'])
f = open(r'AI語譯/_work/review/_re4g2_dups.txt', 'w', encoding='utf-8')
for k, v in sorted(dups.items()):
    f.write("%s %s seg=%s count=%d rows=%s\n" % (k[0], k[1], k[2], v, bykey[k]))
f.close()
print(len(dups))
