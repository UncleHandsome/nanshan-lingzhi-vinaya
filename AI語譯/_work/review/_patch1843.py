# -*- coding: utf-8 -*-
import json
p = '_r2n_spec_1843.json'
d = json.load(open(p, encoding='utf-8-sig'))
fix = {'既然奉行佛陀聖者的威儀': 3, '在次一科說明正確認義中': 4,
       '這種作法超越違越了常規模範': 3, '或者用扁擔挑挑': 3,
       '《五分律》文字較寬漫': 13}
for s in d:
    for it in s['items']:
        if it[1] in fix:
            it[0] = fix[it[1]]
    for v in s['verdicts']:
        if v['seq'] == 2:
            v['seq'] = 3
        elif v['seq'] == 3:
            v['seq'] = 4
        elif v['seq'] == 11:
            v['seq'] = 13
json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('patched')
