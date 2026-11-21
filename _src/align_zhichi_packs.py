# -*- coding: utf-8 -*-
"""資持記 _打包審核 3,577 packs 對 raw 從頭順序對齊。"""
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
    src = han(units[0].get('orig', ''))
    if not src:
        continue
    q = -1
    for n in (20, 12, 8):
        q = h.find(src[:n])
        if q >= 0:
            break
    if q < 0:
        miss += 1
        continue
    items.append((q, x.get('key', f[:-5]), x.get('members') or [], len(src)))
items.sort()
pos = [x[0] for x in items]
order = sum(1 for i in range(1, len(pos)) if pos[i] < pos[i - 1])
# coverage by first-unit length only
iv = [(q, q + n) for q, _, _, n in items]
cover = [0] * len(h)
for a, b in iv:
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
dups = sum(1 for a, b in iv if any(cover[i] > 1 for i in range(a, min(b, len(h)))))
out = {'packs': len(items), 'miss': miss, 'order_break': order, 'gaps': gaps, 'overlaps': dups,
       'items': [{'raw_start': q, 'pack': k, 'members': m, 'length': n} for q, k, m, n in items]}
fp = os.path.join(B, '重作材料_長段', '資持記_打包審核_對齊.json')
json.dump(out, io.open(fp, 'w', encoding='utf-8'), ensure_ascii=False)
lines = ['# 資持記打包審核順序對齊', '',
         '- packs：%d' % len(items),
         '- 對不到 raw：%d' % miss,
         '- 順序倒退：%d' % order,
         '- 缺口：%d' % gaps,
         '- 重疊：%d' % dups, '',
         '| pack | raw | members |', '|:--|--:|:--|']
for q, k, m, n in items[:50]:
    lines.append('| %s | %d | %s |' % (k, q, ','.join(map(str, m))))
md = os.path.join(B, '重作材料_長段', '資持記_打包審核_對齊.md')
io.open(md, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print(len(items), miss, order, gaps, dups)
