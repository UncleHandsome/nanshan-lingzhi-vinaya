# -*- coding: utf-8 -*-
"""Build out_012.json from the manual alignment table."""
import io, os, json, sys
sys.stdout.reconfigure(encoding='utf-8')

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
AD = os.path.join(B, 'AI語譯', '_work', 'align_fix')
J = json.load(io.open(os.path.join(AD, '012.json'), encoding='utf-8'))
items = J['items']
cand = J['cand']
cset = {c['c'] for c in cand}

# 戒 grouping: z -> c
spec = [
    (900, 901, 157),   # 17 牽他出僧房
    (902, 903, 158),   # 18 坐脫脚床
    (904, 908, 159),   # 19 用蟲水
    (909, 910, 160),   # 20 覆屋過三節
    (911, 913, 161),   # 21 輒教尼
    (914, 915, 162),   # 22 與尼說法至日暮
    (916, 916, 163),   # 23 譏教尼人
    (917, 917, 164),   # 24 與非親尼衣
    (918, 918, 165),   # 25 與非親尼作衣
    (919, 921, 166),   # 26 獨與尼屏露坐
    (922, 924, 167),   # 27 與尼期行
    (925, 925, 168),   # 28 與尼同船
    (926, 930, 169),   # 29 食尼歎食
    (931, 932, 170),   # 30 與女人期同行
    (933, 933, 171),   # 31 施一食處過受
    (934, 937, 172),   # 32 展轉食
    (938, 940, 173),   # 33 別眾食 名/相/三相總標
    (941, 941, 175),   #    僧次七緣
    (942, 942, 177),   #    別請
    (943, 943, 179),   #    重釋七緣
    (944, 952, 181),   #    別僧/別乞/別請
    (953, 955, 182),   #    四食處成眾
    (956, 958, 183),   #    五界內不盡集
    (959, 968, 185),   #    不犯開七緣
    (969, 969, 185),   # 中三上 卷題（沿用前）
    (970, 971, 186),   # 34 取歸婦賈客食
    (972, 974, 187),   # 35 足食戒五緣
    (975, 982, 188),   #    食體/五正五似/僧祇八遮
    (983, 985, 189),   #    作餘食法
    (986, 986, 190),   #    不犯
    (987, 987, 191),   # 36 勸足食
    (988, 1005, 192),  # 37 非時食
    (1006, 1008, 193), # 38 食殘宿 名相/四句
    (1009, 1009, 194), #    十誦三相
    (1010, 1011, 195), #    善見轉易
    (1012, 1012, 196), #    無水取食
    (1013, 1014, 197), #    僧祇護淨
    (1015, 1015, 198), #    不犯
    (1016, 1016, 199), # 39 不受食 十門
    (1017, 1017, 200), #    制意
    (1018, 1018, 201), #    能受人
    (1019, 1020, 202), #    所對境
    (1021, 1026, 203), #    所受食
    (1027, 1033, 205), #    受食法
    (1034, 1035, 206), #    食觀
    (1036, 1037, 207), #    正受食法
    (1038, 1039, 208), #    失受法
    (1040, 1040, 209), #    依文解
    (1041, 1043, 210), # 40 索美食
    (1044, 1045, 211), # 41 與外道食
    (1046, 1048, 212), # 42 不囑同利入聚
    (1049, 1049, 213), # 43 食家強坐
]

z2c = {}
for a, b, c in spec:
    for z in range(a, b + 1):
        assert z not in z2c, z
        z2c[z] = c

zs = [it['z'] for it in items]
assert len(zs) == len(set(zs)), 'dup z'
missing = [z for z in zs if z not in z2c]
print('items', len(items), 'mapped', len(z2c), 'missing', missing)
map_ = [{'z': z, 'c': z2c[z]} for z in zs]

# validations
assert len(map_) == len(items)
assert all(m['c'] in cset for m in map_), 'c not in cand'
bad = [(map_[i]['z'], map_[i]['c'], map_[i+1]['z'], map_[i+1]['c'])
       for i in range(len(map_) - 1) if map_[i]['c'] > map_[i+1]['c']]
print('non-monotone:', bad)
from collections import Counter
cnt = Counter(m['c'] for m in map_)
print('distinct c used:', len(cnt), 'range', min(cnt), max(cnt))
gaps = [c for c in range(min(cnt), max(cnt) + 1) if c not in cnt]
print('unused c in range:', gaps)
print('counts:', ' '.join('c%d:%d' % (c, cnt[c]) for c in sorted(cnt)))

io.open(os.path.join(AD, 'out_012.json'), 'w', encoding='utf-8').write(
    json.dumps({'map': map_}, ensure_ascii=False, separators=(',', ':')))
print('written', len(map_))
