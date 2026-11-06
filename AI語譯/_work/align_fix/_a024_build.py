#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build out_024.json : map each 記段 z -> 鈔段 c."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))

# 鈔段索引（cand 下標）：
#  0 序(法軌被時…)            1 就中分二      2 初中分三
#  3 初中《智論》制相敬意      4 二明對緣是非   5 三立敬儀式
#  6 初中敬佛塔法              7 二正明相者    8 次明敬僧法
#  9 次明大小設禮法           10 二明造佛像塔寺法(科)  11 初明造經像法意
# 12 次明造塔法               13 二造寺法     14 因即隨明敬護三衣
# 15 次篇篇題(不用)
groups = [
    (0,  5,  0),   # z0-5   序（含前篇末、釋題、敘意、時弊）
    (6,  13, 3),   # z6-13  制相敬意：《智論》生身/法身、四分三鳥獸、大悲、增一、雜含、智論坐次
    (14, 16, 4),   # z14-16 二明對緣是非：十三難、寶梁八輕、應禮諸文
    (17, 17, 5),   # z17    三立敬儀式分三之科判
    (18, 28, 6),   # z18-28 初中敬佛塔法：佛物、五功德、三禮五輪、繞塔念佛、右遶
    (29, 43, 7),   # z29-43 二正明相者：斥非、敬處別、下床禮佛、三千/十誦、四日、時節、正法久住
    (44, 45, 8),   # z44-45 次明敬僧法
    (46, 52, 9),   # z46-52 次明大小設禮法：母論、五眾相禮、沙彌次第、和南、共坐
    (53, 66, 11),  # z53-66 初明造經像法意：目連圖寫、垂誡、此方傳像、失法、靈應、善見
    (67, 78, 12),  # z67-78 次明造塔法：雜心、梵福、造塔諸法、善生、無垢經、涅槃
    (79, 84, 13),  # z79-84 二造寺法：寺誥、非法、無法、勸修、闍王
    (85, 91, 14),  # z85-91 敬護三衣、威儀念法、王臣待遇
]

d = json.load(open(os.path.join(HERE, '024.json'), encoding='utf-8'))
n = len(d['items'])
nc = len(d['cand'])
mp = {}
for a, b, c in groups:
    for z in range(a, b + 1):
        mp[z] = c
assert sorted(mp) == list(range(n)), (len(mp), n)
vals = [mp[z] for z in range(n)]
assert all(0 <= v < nc for v in vals)
assert all(vals[i] <= vals[i + 1] for i in range(n - 1)), 'not monotone'
out = {'map': [{'z': z, 'c': mp[z]} for z in range(n)]}
with open(os.path.join(HERE, 'out_024.json'), 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, separators=(',', ':'))
print('items', n, 'groups', len(groups), 'used c', sorted(set(vals)))
