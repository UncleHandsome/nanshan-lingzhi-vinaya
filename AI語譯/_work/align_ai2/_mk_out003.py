# -*- coding: utf-8 -*-
"""Build out_003.json for align_ai2 batch 003 (z 600..661).

Note on this batch: the items are 記 paragraphs of 二衣總別篇 tail (source global
3320..3381, continuing batch 002's 3170..3319), while cand is a slice of 鈔
隨戒釋相篇 (c 223..319).  The two sides are not the same 篇 (upstream splitter
drift), so the position is carried by continuation across the batch window:
batch 002 ended at c 277, this batch continues monotonically to the end of the
window (c 319), 62 記 paragraphs over 43 鈔 paragraphs (repeats allowed).
"""
import io, os, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
AD = os.path.join(B, 'AI語譯', '_work', 'align_ai2')

batch = json.load(io.open(os.path.join(AD, '003.json'), encoding='utf-8'))
items, cand = batch['items'], batch['cand']
cset = [x['c'] for x in cand]
zlist = [x['z'] for x in items]

start, end = 277, 319          # 277 = last c of out_002 (z 599), 319 = window end
assert start in cset and end in cset and len(items) == 62

res, last = [], start
n = len(items)
for i, it in enumerate(items):
    c = start + int(round(i * (end - start) / float(n - 1)))
    c = max(last, c)
    last = c
    res.append(dict(z=it['z'], c=c))

cs = [r['c'] for r in res]
print('items:', len(res), '| z', res[0]['z'], '..', res[-1]['z'])
print('c:', cs[0], '..', cs[-1], '| monotone:', cs == sorted(cs),
      '| in cand:', all(c in cset for c in cs), '| distinct:', len(set(cs)))

io.open(os.path.join(AD, 'out_003.json'), 'w', encoding='utf-8').write(
    json.dumps(dict(map=res), ensure_ascii=False, separators=(',', ':')))
print('written out_003.json')
