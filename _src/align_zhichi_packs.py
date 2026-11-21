# -*- coding: utf-8 -*-
"""資持記 _打包審核 3,576 packs 對 raw 從頭順序對齊（用全部 units 定 pack 範圍）。"""
import io
import json
import os
import re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
P = os.path.join(B, '測試', '重譯', '資持記', '_打包審核')
R = os.path.join(B, 'TXT', '資持記')


def han(s):
    s = re.sub(r'^(?:【[^】]+】)+', '', str(s).strip())
    return ''.join(re.findall(r'[\u4e00-\u9fff]', s))


raw = ''
maps = []
for f in sorted(os.listdir(R)):
    if not f.endswith('.txt'):
        continue
    t = io.open(os.path.join(R, f), encoding='utf-8').read()
    a = len(raw)
    raw += t
    maps.append((a, len(raw), f))
h = ''
for c in raw:
    if '\u4e00' <= c <= '\u9fff':
        h += c

items = []
miss = 0
partial = 0
for f in sorted(os.listdir(P)):
    if not f.endswith('.json'):
        continue
    try:
        x = json.load(io.open(os.path.join(P, f), encoding='utf-8'))
    except Exception:
        continue
    units = x.get('units') or []
    if not units:
        continue
    qs = []
    for u in units:
        s = han(u.get('orig', ''))
        if not s:
            continue
        q = -1
        for n in (20, 12, 8):
            q = h.find(s[:n])
            if q >= 0:
                break
        if q >= 0:
            qs.append((q, q + len(s)))
        else:
            partial += 1
    if not qs:
        miss += 1
        continue
    a = min(q for q, _ in qs)
    b = max(e for _, e in qs)
    items.append((a, b, x.get('key', f[:-5]), x.get('members') or [], len(qs), len(units)))
items.sort()
pos = [x[0] for x in items]
order = sum(1 for i in range(1, len(pos)) if pos[i] < pos[i - 1])
cover = [0] * len(h)
for a, b, *_ in items:
    for i in range(a, min(b, len(h))):
        cover[i] += 1
gaps = 0
i = 0
while i < len(h):
    if cover[i] == 0:
        j = i
        while j < len(h) and cover[j] == 0:
            j += 1
        if j - i >= 20:
            gaps += 1
        i = j
    else:
        i += 1
dups = sum(1 for a, b, *_ in items if any(cover[i] > 1 for i in range(a, min(b, len(h)))))
out = {'packs': len(items), 'miss': miss, 'partial_units': partial, 'order_break': order,
       'gaps': gaps, 'overlaps': dups,
       'items': [{'raw_start': a, 'raw_end': b, 'pack': k, 'members': m, 'units_found': nf, 'units': n}
                 for a, b, k, m, nf, n in items]}
json.dump(out, io.open(os.path.join(B, '重作材料_長段', '資持記_打包審核_對齊.json'), 'w', encoding='utf-8'), ensure_ascii=False)
lines = ['# 資持記打包審核順序對齊', '',
         '- packs：%d' % len(items),
         '- 對不到 pack：%d' % miss,
         '- 部分 unit 對不到：%d' % partial,
         '- 順序倒退：%d' % order,
         '- 缺口：%d' % gaps,
         '- 重疊：%d' % dups, '',
         '| pack | raw 起 | raw 迄 | units |', '|:--|--:|--:|--:|']
for a, b, k, m, nf, n in items[:50]:
    lines.append('| %s | %d | %d | %d/%d |' % (k, a, b, nf, n))
io.open(os.path.join(B, '重作材料_長段', '資持記_打包審核_對齊.md'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print(len(items), miss, partial, order, gaps, dups)
