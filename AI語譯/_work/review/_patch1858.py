# -*- coding: utf-8 -*-
import json
p = '_r2n_spec_1858.json'
d = json.load(open(p, encoding='utf-8-sig'))
drop = ['經文敘述戒定慧三學互為緣起', '罪念始終留在心中', '若不能防範其成為未來的習氣']
for s in d:
    s['items'] = [it for it in s['items'] if it[1] not in drop]
json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('patched')
