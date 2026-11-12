# -*- coding: utf-8 -*-
import json
p = '_r2n_spec_1849.json'
d = json.load(open(p, encoding='utf-8-sig'))
for s in d:
    s['items'] = [it for it in s['items'] if '燒烤' not in it[1]]
json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('patched')
