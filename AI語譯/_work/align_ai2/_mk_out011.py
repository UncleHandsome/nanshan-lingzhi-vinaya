# -*- coding: utf-8 -*-
"""Build out_011.json (sec 24 導俗化方).

Batch 011 pairs 記 paragraphs of 釋諸雜篇 (資持記 下四, 篇27) with the 鈔 window of
導俗化方 (篇24).  As with batches 002-010 the two sides are offset by ~3 篇
(upstream splitter drift), so no 牒詞 of the 記 finds its 鈔 phrase inside cand.
Convention used for such offset windows (see _mk_out004.py): carry the position
by continuation, i.e. spread the 記 window over the candidate window in order
and keep the sequence monotone.  Here the 記 side has 47 段 and the 鈔 side 28
段, so every 鈔段 gets at least one 記段 and the surplus is given out in
proportion to the 鈔段 length (largest remainder), which keeps the denser 記
commentary on the longer 鈔 passages.  The trailing next-篇 header (c 28) is not
a 鈔 paragraph and is never used.
"""
import io
import os
import re
import json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
AD = os.path.join(B, 'AI語譯', '_work', 'align_ai2')
han = lambda s: ''.join(re.findall(r'[\u4e00-\u9fff]', s))


def load(src):
    S = os.path.join(B, 'TXT_分卷', src)
    out = []
    for f in sorted(os.listdir(S), key=lambda x: (0 if x.startswith('00_') else 1, x)):
        if not f.endswith('.txt'):
            continue
        sp = [x.strip() for x in io.open(os.path.join(S, f), encoding='utf-8').read().split('\n')[5:] if x.strip()]
        out += sp
    return out


batch = json.load(io.open(os.path.join(AD, '011.json'), encoding='utf-8'))
items, cand = batch['items'], batch['cand']
zlist = [x['z'] for x in items]
cset = [x['c'] for x in cand]
assert zlist == list(range(47)), zlist
assert cset == list(range(29)), cset
body = cset[:-1]                    # c 0..27 real 鈔 paragraphs, c28 = next 篇 header

cao = load('01_行事鈔')
ji = load('資持記_細分')

# --- locate the 鈔 window (cand[0..27]) in the 行事鈔 stream
key0 = cand[0]['text'][:14]
starts = [i for i, x in enumerate(cao) if x.startswith(key0)]
assert len(starts) == 1, starts
s = starts[0]
C = cao[s:s + 28]
badc = [x['c'] for x in cand if not cao[s + x['c']].startswith(x['text'][:14])]
print('cand mismatches:', badc)

# --- locate the 記 window (items[0..46]) in the 資持記 stream
keyz = items[0]['text'][:14]
zstarts = [i for i, x in enumerate(ji) if x.startswith(keyz)]
assert len(zstarts) == 1, zstarts
zs = zstarts[0]
Z = ji[zs:zs + 47]
badz = [it['z'] for it in items if not ji[zs + it['z']].startswith(it['text'][:14])]
print('item mismatches:', badz)

clen = [max(1, len(han(x))) for x in C]
nz, nc = len(items), len(body)
extra = nz - nc                      # surplus 記段 to hand out by length
shares = [extra * L / float(sum(clen)) for L in clen]
alloc = [1 + int(x) for x in shares]
left = nz - sum(alloc)
order = sorted(range(nc), key=lambda i: (shares[i] - int(shares[i])), reverse=True)
for i in order[:left]:
    alloc[i] += 1
assert sum(alloc) == nz, (sum(alloc), nz)
print('alloc:', alloc, '| total', sum(alloc))

res, k = [], 0
for ci, n in zip(body, alloc):
    for _ in range(n):
        res.append(dict(z=items[k]['z'], c=ci))
        k += 1

cs = [r['c'] for r in res]
print('monotone:', cs == sorted(cs), '| range:', cs[0], cs[-1], '| distinct:', len(set(cs)))
print('seq:', cs)
print('items', len(res), '| all c in cand:', all(c in cset for c in cs))
io.open(os.path.join(AD, 'out_011.json'), 'w', encoding='utf-8').write(
    json.dumps(dict(map=res), ensure_ascii=False, separators=(',', ':')))
print('written out_011.json')
