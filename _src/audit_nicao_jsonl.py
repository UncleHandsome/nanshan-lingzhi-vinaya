# -*- coding: utf-8 -*-
"""尼鈔：稽核 定稿/nicao.jsonl 的覆蓋、缺口、重疊、未定位。"""
import io, json, os, re, sys
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
raw = io.open(os.path.join(B, 'TXT', '04_四分律比丘尼鈔.txt'), encoding='utf-8').read()
h = ''
mp = []
for i, c in enumerate(raw):
    if '\u4e00' <= c <= '\u9fff':
        h += c
        mp.append(i)

p = sys.argv[1] if len(sys.argv) > 1 else os.path.join(B, '定稿', 'nicao.jsonl')
rows = [json.loads(x) for x in io.open(p, encoding='utf-8') if x.strip()]
print('rows', len(rows))
print('keys uniq', len(set(r['key'] for r in rows)))
print('located', sum(1 for r in rows if r.get('raw_start', -1) >= 0))
print('unlocated', sum(1 for r in rows if r.get('raw_start', -1) < 0))
print('no trans', sum(1 for r in rows if not r.get('translation', '').strip()))

iv = sorted((r['raw_start'], r['raw_end']) for r in rows if r.get('raw_start', -1) >= 0)
# overlaps (strict; touching endpoints not overlap)
ov = []
maxend = -1
maxrow = None
for r in sorted(rows, key=lambda x: (x.get('raw_start', -1), x.get('raw_end', -1))):
    a, b = r.get('raw_start', -1), r.get('raw_end', -1)
    if a < 0:
        continue
    if a < maxend:
        ov.append((r['key'], a, b, maxend))
    if b > maxend:
        maxend = b
print('overlap rows', len(ov))
for x in ov[:40]:
    print('  OV', x)

cover = [0] * len(h)
for a, b in iv:
    for i in range(a, min(b, len(h))):
        cover[i] += 1
gaps = []
i = 0
while i < len(h):
    if cover[i] == 0:
        j = i
        while j < len(h) and cover[j] == 0:
            j += 1
        gaps.append((i, j))
        i = j
    else:
        i += 1
print('gaps', len(gaps), 'gap chars total', sum(b - a for a, b in gaps))
for a, b in gaps[:60]:
    print('  GAP', a, b, b - a, repr(h[a:b][:50]))
print('dup count', cover.count(1) if False else '')
multi = sum(1 for x in cover if x > 1)
print('covered chars', sum(1 for x in cover if x > 0), '/', len(h), 'multi-covered', multi)
