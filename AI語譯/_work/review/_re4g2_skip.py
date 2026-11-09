# -*- coding: utf-8 -*-
import json, collections
rows = json.load(open(r'AI語譯/_work/review/_re4g2_rows.json', encoding='utf-8'))
plan = {p['n']: p for p in json.load(open(r'AI語譯/_work/review/_re4g2_plan.json', encoding='utf-8'))}
skip = {11, 62, 68, 112}
f = open(r'AI語譯/_work/review/_re4g2_skip.txt', 'w', encoding='utf-8')
tot = collections.Counter(d['book'] for d in rows)
skc = collections.Counter()
for d in rows:
    n = d['_n']
    if n in skip or plan[n]['kind'] == 'NOSUG':
        skc[d['book']] += 1
        f.write("%d\t%s\t%s\tseg=%s\t%s\n" % (n, d['book'], d['chunk'], d['seg'],
                'applied' if n in skip else 'nosug'))
f.write("TOTAL %s\n" % dict(tot))
f.write("SKIP %s\n" % dict(skc))
f.close()
