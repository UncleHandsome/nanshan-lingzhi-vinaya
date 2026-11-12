# -*- coding: utf-8 -*-
import json
p = '_r2n_spec_1826.json'
d = json.load(open(p, encoding='utf-8-sig'))
for s in d:
    for it in s['items']:
        if '十歲曾嫁' in it[1] or '具備這兩種因緣' in it[1]:
            it[0] = 4
        if '或者在兩年學戒期中' in it[1]:
            it[0] = 8
        if '這些都屬於同一個科律' in it[1]:
            it[0] = 14
json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('patched')
