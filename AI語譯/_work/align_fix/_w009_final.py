# -*- coding: utf-8 -*-
"""產生 out_009.json：批次 009（篇14 隨戒釋相 z450-599）記段→鈔段對齊。"""
import io, os, json, sys
sys.stdout.reconfigure(encoding='utf-8')
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\align_fix'
j = json.load(io.open(os.path.join(D, '009.json'), encoding='utf-8'))
items = j['items']
cand = j['cand']
d = json.load(io.open(os.path.join(D, '_w009_data.json'), encoding='utf-8'))
J, C = d['ji'], d['cao']

# (該鈔段起始 z, c)
seg = [
    (450, 59),   # 四重物（五錢三解、正判、善見堈中、五事）
    (459, 60),   # 二以義門六句
    (462, 61),   # 五離本處（十句、十三處）
    (471, 62),   # 結示勸修
    (474, 63),   # 三明不犯（五想、七法）
    (475, 64),   # 第三殺人戒
    (490, 65),   # 第四大妄語戒
    (497, 66),   # 僧殘第一 故失精戒
    (505, 67),   # 第二 摩觸女人戒
    (519, 68),   # 第三 與女人麁語戒
    (523, 69),   # 第四 向女歎身索供戒
    (525, 70),   # 第五 媒人戒
    (533, 71),   # 第六 無主僧不處分過量房戒
    (537, 72),   # 佛搩手尺量
    (546, 73),   # 難處、妨處
    (559, 74),   # 第七 有主僧不處分房戒
    (562, 75),   # 第八 無根重罪謗他戒
    (567, 76),   # 第九 假根謗戒
    (569, 77),   # 第十 破僧違諫戒
    (574, 78),   # 第十一 助破僧違諫戒
    (575, 79),   # 第十二 污家擯謗違僧諫戒
    (581, 80),   # 第十三 惡性拒僧違諫戒
    (584, 81),   # 二不定 總標
    (585, 82),   # 初 屏處不定
    (588, 83),   # 後 露處不定
    (589, 85),   # 三十捨墮第一 長衣過限戒
    (594, 86),   # 長衣戒 釋諸緣（應量、說淨、過日等）
    (600, 87),   # 哨兵（下一段，不含）
]
m = {}
for i, (z0, c) in enumerate(seg[:-1]):
    for z in range(z0, seg[i + 1][0]):
        m[z] = c

# ---- 驗證 ----
assert sorted(m) == list(range(450, 600)), 'z 範圍不符'
assert len(m) == len(items) == 150, (len(m), len(items))
zs = [it['z'] for it in items]
assert zs == list(range(450, 600)), 'items z 不連續'
cs = [m[z] for z in zs]
assert all(0 <= c < len(cand) for c in cs), 'c 超出 cand'
assert all(cs[i] <= cs[i + 1] for i in range(len(cs) - 1)), 'c 倒退'
# 每個 c 必須是 cand 內實際存在的 index
cset = set(x['c'] for x in cand)
assert all(c in cset for c in cs)
# 抽樣核對 記/鈔 原文頭
print('first/last z', zs[0], zs[-1], 'n', len(cs), 'c range', min(cs), max(cs))

out = {'map': [{'z': z, 'c': m[z]} for z in zs]}
with io.open(os.path.join(D, 'out_009.json'), 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, separators=(',', ':'))
print('wrote out_009.json bytes', os.path.getsize(os.path.join(D, 'out_009.json')))
# 分段摘要
prev = None
for z in zs:
    if m[z] != prev:
        print('  z%-4d -> c%-3d  %s' % (z, m[z], C[m[z]][:38]))
        prev = m[z]
