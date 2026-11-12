# -*- coding: utf-8 -*-
import json
p = '_r2n_spec_1870.json'
d = json.load(open(p, encoding='utf-8-sig'))
for s in d:
    for it in s['items']:
        if it[1].startswith('第五、沒有五種過失'):
            it[0] = 9
        if it[1].startswith('蚊蟲螞蟻等生物'):
            it[1] = '惱害之處甚多'
            it[2] = '（住此）惱害傷損牠們的情形很多'
json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('patched')
