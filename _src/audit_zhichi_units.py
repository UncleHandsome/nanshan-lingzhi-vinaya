# -*- coding: utf-8 -*-
"""資持記 pack：逐 unit 實際區間檢查，不用 pack min–max。"""
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
for f in sorted(os.listdir(R)):
    if f.endswith('.txt'):
        raw += io.open(os.path.join(R, f), encoding='utf-8').read()
h = ''
for c in raw:
    if '\u4e00' <= c <= '\u9fff':
        h += c

packs = []
miss = 0
for f in sorted(os.listdir(P)):
    if not f.endswith('.json'):
        continue
    try:
        x = json.load(io.open(os.path.join(P, f), encoding='utf-8'))
    except Exception:
        continue
    us = []
    for i, u in enumerate(x.get('units') or []):
        s = han(u.get('orig', ''))
        if not s:
            continue
        q = -1
        for n in (20, 12, 8):
            q = h.find(s[:n])
            if q >= 0:
                break
        if q < 0:
            miss += 1
            continue
        us.append((q, q + len(s), u.get('lab', ''), i))
    if us:
        packs.append((x.get('key', f[:-5]), us))

units = [(a, b, k) for k, us in packs for a, b, lab, i in us]
cover = [0] * len(h)
for a, b, k in units:
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
dups = sum(1 for a, b, k in units if any(cover[i] > 1 for i in range(a, min(b, len(h)))))
# pack-level overlap: any unit interval overlaps unit from another pack
intervals = []
for k, us in packs:
    for a, b, lab, i in us:
        intervals.append((a, b, k))
intervals.sort()
overlap_packs = set()
active = []
for a, b, k in intervals:
    active = [(x, y, kk) for x, y, kk in active if y > a]
    for x, y, kk in active:
        if kk != k:
            overlap_packs.add(k)
            overlap_packs.add(kk)
    active.append((a, b, k))
print('packs', len(packs), 'units', len(units), 'miss', miss, 'gaps', gaps, 'unit_overlaps', dups, 'overlap_packs', len(overlap_packs))
json.dump({'packs': len(packs), 'units': len(units), 'miss': miss, 'gaps': gaps,
           'unit_overlaps': dups, 'overlap_packs': len(overlap_packs)},
          io.open(os.path.join(B, '重作材料_長段', '資持記_unit檢查.json'), 'w', encoding='utf-8'), ensure_ascii=False)
