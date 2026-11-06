#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
out = []
for name in ['018', '013', '017']:
    d = json.load(open(os.path.join(HERE, name + '.json'), encoding='utf-8'))
    o = json.load(open(os.path.join(HERE, 'out_' + name + '.json'), encoding='utf-8'))
    mp = {x['z']: x['c'] for x in o['map']}
    out.append(f'===== {name}: items={len(d["items"])} cand={len(d["cand"])} ====')
    zs = [it['z'] for it in d['items']]
    out.append('first z=%s last z=%s' % (zs[0], zs[-1]))
    for it in d['items']:
        z = it['z']
        out.append(f'z{z} -> c{mp.get(z)} :: {it["text"][:50]}')
    out.append('--- cand heads')
    for cb in d['cand']:
        out.append(f'c{cb["c"]} :: {cb["text"][:50]}')
open(os.path.join(HERE, '_a024_cmp.txt'), 'w', encoding='utf-8').write('\n'.join(out))
print('ok')
