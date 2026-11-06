# -*- coding: utf-8 -*-
"""建立/檢核 009 批次對齊草案：列出每個 c 起點的前後文。"""
import io, os, json, sys
sys.stdout.reconfigure(encoding='utf-8')
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\align_fix'
d = json.load(io.open(os.path.join(D, '_w009_data.json'), encoding='utf-8'))
J, C = d['ji'], d['cao']

# (起始 z, c)
segs = [
    (450, 59), (459, 60), (462, 61), (471, 62), (474, 63), (475, 64),
    (490, 65), (497, 66), (505, 67), (518, 68), (523, 69), (525, 70),
    (533, 71), (536, 72), (546, 73), (559, 74), (562, 75), (567, 76),
    (569, 77), (574, 78), (575, 79), (581, 80), (584, 81), (585, 82),
    (588, 83), (589, 85), (594, 86), (600, 87),
]
m = {}
for i, (z0, c) in enumerate(segs[:-1]):
    z1 = segs[i + 1][0]
    for z in range(z0, z1):
        m[z] = c
assert sorted(m) == list(range(450, 600)), (len(m), sorted(m)[:3], sorted(m)[-3:])
print('count', len(m))
for i, (z0, c) in enumerate(segs[:-1]):
    print('\n=== z%d -> c%d ===' % (z0, c))
    if z0 > 450:
        print('  prev tail: ...' + J[z0 - 1][-70:])
    print('  head: ' + J[z0][:130])
json.dump({'map': [{'z': z, 'c': c} for z, c in m.items()]},
          io.open(os.path.join(D, 'out_009.json'), 'w', encoding='utf-8'), ensure_ascii=False)
print('\nwrote out_009.json')
