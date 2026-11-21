# -*- coding: utf-8 -*-
"""驗證輸出的 定稿/xingshichao.jsonl（獨立重算，不信任建置腳本）。"""
import io, json, os, re
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
RAW = io.open(os.path.join(B, 'TXT', '01_四分律刪繁補闕行事鈔.txt'), encoding='utf-8').read()
H = ''.join(re.findall(r'[\u4e00-\u9fff]', RAW))
MP = [i for i, c in enumerate(RAW) if '\u4e00' <= c <= '\u9fff']
def han(s): return ''.join(re.findall(r'[\u4e00-\u9fff]', s))
p = os.path.join(B, '定稿', 'xingshichao.jsonl')
rows = [json.loads(x) for x in io.open(p, encoding='utf-8') if x.strip()]
print('rows', len(rows))
print('fields', list(rows[0].keys()))
print('key unique', len({r['key'] for r in rows}) == len(rows))
print('book/book_id', {r['book'] for r in rows}, {r['book_id'] for r in rows})
print('label', {r['label'] for r in rows})
print('revised', sum(1 for r in rows if r['revised']))

bad = []
for r in rows:
    if r['raw_start'] < 0 or r['raw_end'] <= r['raw_start']:
        bad.append((r['key'], 'span'))
        continue
    if r['raw_end'] > len(H):
        bad.append((r['key'], 'oob')); continue
    if han(r['source']) != H[r['raw_start']:r['raw_end']]:
        bad.append((r['key'], 'source!=raw'))
    if not r['translation'] or not r['segments'][0]['translation']:
        bad.append((r['key'], 'empty tr'))
    if not r['translation'].startswith('【%s】' % r['label']):
        bad.append((r['key'], 'tr label'))
    if r['segments'][0]['source'] != r['source']:
        bad.append((r['key'], 'seg src'))
    if r['segments'][0]['label'] != r['label']:
        bad.append((r['key'], 'seg label'))
print('per-row problems', len(bad), bad[:10])

# 單調
prev = -1; back = 0
for r in rows:
    if r['raw_start'] < prev: back += 1
    prev = max(prev, r['raw_start'])
print('非單調遞增', back)
# 覆蓋
cover = [0] * (len(H) + 1)
for r in rows:
    for i in range(r['raw_start'], min(r['raw_end'], len(H))):
        cover[i] += 1
print('overlap chars', sum(1 for c in cover[:len(H)] if c > 1))
runs = []
i = 0
while i < len(H):
    if cover[i] == 0:
        j = i
        while j < len(H) and cover[j] == 0: j += 1
        runs.append((i, j, j - i)); i = j
    else: i += 1
print('uncovered runs', len(runs), 'chars', sum(r[2] for r in runs), '| >=20:', [r for r in runs if r[2] >= 20])
# 標籤殘留
cont = [r['key'] for r in rows if '【後文背景' in r['segments'][0]['translation'] or '【裁決' in r['segments'][0]['translation']]
print('背景/裁決殘留', len(cont))
# 大小
sz = sorted(len(han(r['source'])) for r in rows)
print('source len min/med/p95/max', sz[0], sz[len(sz)//2], sz[int(len(sz)*0.95)], sz[-1])
print('rows with source len < 20:', sum(1 for x in sz if x < 20))
# 抽樣
for key in ('01', '109', '220', '1026', 'P0001', 'P0002'):
    for r in rows:
        if r['key'] == key:
            print('---', key, r['raw_start'], r['raw_end'], r['chunk'], r['origin'], r['picksrc'])
            print('  S:', r['source'][:150])
            print('  T:', r['segments'][0]['translation'][:150])
            break
print('前 3 筆：')
for r in rows[:3]:
    print(' ', r['key'], r['raw_start'], r['raw_end'], '|', r['source'][:40], '|', r['segments'][0]['translation'][:50])
