# -*- coding: utf-8 -*-
import io
import json

d = json.load(io.open('014.json', encoding='utf-8'))
o = json.load(io.open('out_014.json', encoding='utf-8'))
m = o['map']
cs = [x['c'] for x in m]
zs = [x['z'] for x in m]
cset = [c['c'] for c in d['cand']]
print('items', len(d['items']), 'rows', len(m))
print('z contiguous', zs == list(range(len(d['items']))))
print('monotone', all(cs[i] <= cs[i + 1] for i in range(len(cs) - 1)))
print('all c in cand', all(c in cset for c in cs), 'range', min(cs), max(cs))
print('first', m[0], 'last', m[-1])
print('keys', sorted(o.keys()))
