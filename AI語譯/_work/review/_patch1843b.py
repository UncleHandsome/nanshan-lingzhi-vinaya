# -*- coding: utf-8 -*-
import json
p = '_r2n_spec_1843.json'
d = json.load(open(p, encoding='utf-8-sig'))
fix = {'或者用扁擔挑挑': 5, '如果不是這樣，出家豈不就成了徒勞無益之事嗎': 8,
       '由此可知，衣服的相貌普遍具有正衣與從衣的差別': 16}
for s in d:
    for it in s['items']:
        if it[1] in fix:
            it[0] = fix[it[1]]
    for v in s['verdicts']:
        if v['seq'] == 7:
            v['seq'] = 8
        if v['seq'] == 15:
            v['seq'] = 16
json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('patched2')
