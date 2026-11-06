# -*- coding: utf-8 -*-
import io, json, os

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'

# 篇8：鈔49 起首改記137（讓記136尾巴與記137都歸鈔49之前）
bp = os.path.join(B, 'AI語譯', '_work', 'pian_bounds', 'bounds_篇08.json')
d = json.load(io.open(bp, encoding='utf-8-sig'))
for x in d['bounds']:
    if x['c'] == 49:
        x['n'] = 137
json.dump(d, io.open(bp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# 篇9：記028 三切、記029 切、鈔15 後移
mp = os.path.join(B, 'AI語譯', '_work', 'pian_manual', '篇09.json')
m = json.load(io.open(mp, encoding='utf-8-sig'))
m['splits'] = [e for e in m['splits'] if int(e['n']) not in (28, 29)]
m['splits'] += [
    {'n': 28, 'base': 12, 'markers': ['制意中，初敘由', '二中，《四分》'], 'targets': [12, 13, 14]},
    {'n': 29, 'base': 14, 'markers': ['第三列名中。'], 'targets': [14, 15]},
]
json.dump(m, io.open(mp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

bp9 = os.path.join(B, 'AI語譯', '_work', 'pian_bounds', 'bounds_篇09.json')
d9 = json.load(io.open(bp9, encoding='utf-8-sig'))
for x in d9['bounds']:
    if x['c'] == 15:
        x['n'] = 30
json.dump(d9, io.open(bp9, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('patched 8/9')
