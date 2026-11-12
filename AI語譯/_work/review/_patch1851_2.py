# -*- coding: utf-8 -*-
import json
p = '_r2n_spec_1851.json'
d = json.load(open(p, encoding='utf-8-sig'))
m = {'說藏宿包含兩種': 2, '這在道理上是毫無偏失的': 6,
     '在受別請與充足食等戒相上': 9, '非受請食、非正食、非充足食': 9,
     '違背別請戒與充足再食戒': 10,
     '是指未曾受持而擅自觸摸抓取的食物': 14,
     '是指其餘三種藥物曾受持而違背時限，並非他人如法布施而自己取食之物': 14,
     '或者「可食」是指可以食用之物': 17}
for s in d:
    for it in s['items']:
        if it[1] in m:
            it[0] = m[it[1]]
json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

p = '_r2n_spec_1852.json'
d = json.load(open(p, encoding='utf-8-sig'))
for s in d:
    for it in s['items']:
        if it[1] == '實體不可發生錯謬':
            it[0] = 7
json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('patched')
