# -*- coding: utf-8 -*-
import json
p = '_r2n_spec_1830.json'
d = json.load(open(p, encoding='utf-8-sig'))
for s in d:
    for it in s['items']:
        if '自劉宋以前' in it[1]:
            it[0] = 15
        if '而比丘尼則僅在單一部眾' in it[1]:
            it[0] = 16
json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('patched')
