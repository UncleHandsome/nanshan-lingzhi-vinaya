# -*- coding: utf-8 -*-
import io, json, collections
raw = io.open(r'AI語譯/_work/review/fix_re4_g2.tsv', encoding='utf-8').read().split('\n')[:-1]
rows = [l.split('\t') for l in raw]
rows0 = json.load(open(r'AI語譯/_work/review/_re4g2_rows.json', encoding='utf-8'))
plan = {p['n']: p for p in json.load(open(r'AI語譯/_work/review/_re4g2_plan.json', encoding='utf-8'))}
skip = {11, 62, 68, 112}
expect = []
for d in rows0:
    n = d['_n']
    if n in skip or plan[n]['kind'] == 'NOSUG':
        continue
    expect.append((d['book'], d['chunk'], d['seg']))
got = [(r[0], r[1], r[2]) for r in rows]
print('expect', len(expect), 'got', len(got), 'same', expect == got)
# consistency within key
bykey = collections.defaultdict(set)
for r in rows:
    bykey[(r[0], r[1], r[2])].add(r[3])
print('inconsistent keys', [k for k, v in bykey.items() if len(v) > 1])
print('distinct', len(bykey))
