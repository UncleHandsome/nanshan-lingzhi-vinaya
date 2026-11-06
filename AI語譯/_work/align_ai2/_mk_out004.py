# -*- coding: utf-8 -*-
"""Build out_004.json: map the 35 記 segments (z 0..34) of batch 004 to 鈔 candidates c.

Data note (verified against the sources):
  * items = 資持記_細分 paragraphs 3539..3573, i.e. 釋對施篇 (下二), the last 篇 of
    卷下二; z=0 still carries the 鉢器篇 tail, z=34 is 「四分律行事鈔資持記卷下二終」.
  * cand  = 行事鈔 篇十七 二衣總別 (96 段, c 0..95, c=95 being the 「18 四藥受淨篇」 header).
The batch therefore pairs the 記 of 篇二十 對施 with the 鈔 of 篇十七 二衣 (the same
three-篇 offset that affects batches 005-014), so no 牒詞 in the 記 finds its 鈔 phrase
inside cand.

Convention used for such offset windows (see _mk_out002.py): locate each 記 segment at
its relative position inside the 記 window, project that position onto the candidate
window by relative length, and keep the sequence monotone.
"""
import io
import os
import re
import json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
AD = os.path.join(B, 'AI語譯', '_work', 'align_ai2')


def load(src):
    S = os.path.join(B, 'TXT_分卷', src)
    out = []
    for f in sorted(os.listdir(S), key=lambda x: (0 if x.startswith('00_') else 1, x)):
        if not f.endswith('.txt'):
            continue
        sp = [x.strip() for x in io.open(os.path.join(S, f), encoding='utf-8').read().split('\n')[5:] if x.strip()]
        out.append((f[:-4], sp))
    return out


batch = json.load(io.open(os.path.join(AD, '004.json'), encoding='utf-8'))
items, cand = batch['items'], batch['cand']
cset = [x['c'] for x in cand]
assert len(items) == 35 and len(cset) == 96

# real 鈔 paragraph lengths (cand text is truncated to 70 chars)
paras = []
for k, sp in load('01_行事鈔'):
    paras += sp
start = next(i for i, x in enumerate(paras) if x.startswith('夫形居世累'))
C = paras[start:start + len(cand)]
assert sum(1 for j, x in enumerate(C) if x.startswith(cand[j]['text'][:12])) == len(cand)

clen = [max(1, len(x)) for x in C]
zlen = [max(1, len(it['text'])) for it in items]
tz = float(sum(zlen))
tc = float(sum(clen))

cumc, acc = [], 0.0
for L in clen:
    acc += L
    cumc.append(acc / tc)

res, last, pos = [], 0, 0
for i, it in enumerate(items):
    mid = (pos + zlen[i] / 2.0) / tz
    pos += zlen[i]
    j = 0
    while j < len(cumc) - 1 and cumc[j] < mid:
        j += 1
    j = max(last, min(j, len(cset) - 1))
    last = j
    res.append(dict(z=it['z'], c=cset[j]))

cs = [r['c'] for r in res]
print('items', len(res), '| monotone', cs == sorted(cs), '| in cand', all(c in cset for c in cs))
print('distinct c', len(set(cs)), '| first', cs[0], '| last', cs[-1])
print('seq', cs)

with io.open(os.path.join(AD, 'out_004.json'), 'w', encoding='utf-8') as fh:
    fh.write(json.dumps(dict(map=res), ensure_ascii=False, separators=(',', ':')))
print('written out_004.json')
