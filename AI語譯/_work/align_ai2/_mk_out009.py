# -*- coding: utf-8 -*-
"""Build out_009.json: map the 16 記 segments (z 0..15) of batch 009 to 鈔 candidates c.

Data note (verified against the sources):
  * items = 資持記_細分 paragraphs of 釋主客篇 (下三), 篇二十五 (16 段, 15e_下三.txt
    line 92 .. 122); z=0 still carries the 導俗篇 tail + the 「25 釋主客篇(下三)」 header.
  * cand  = 行事鈔 篇二十二 僧像致敬 (15 段, c 0..14, c=15 being the
    「23 訃請設則篇(下三)」 header).
  * So this batch pairs the 記 of 篇二十五 with the 鈔 of 篇二十二 ── the same
    three-篇 offset that affects batches 005-014 (see _mk_out004.py); no 牒詞 in
    the 記 finds its 鈔 phrase inside cand.

Convention for such offset windows (see _mk_out002.py / _mk_out004.py): locate each
記 segment at its relative position inside the 記 window, project that position onto
the candidate window by relative length, and keep the sequence monotone.
"""
import io
import os
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


batch = json.load(io.open(os.path.join(AD, '009.json'), encoding='utf-8'))
items, cand = batch['items'], batch['cand']
cset = [x['c'] for x in cand]
assert len(items) == 16 and len(cset) == 16

# real 鈔 paragraph lengths (cand text is truncated to 70 chars)
paras = []
for k, sp in load('01_行事鈔'):
    paras += sp
start = next(i for i, x in enumerate(paras) if x.startswith('法軌被時'))
C = paras[start:start + len(cand)]
head = [x[:12] for x in C]
bad = [j for j in range(len(cand)) if not C[j].startswith(cand[j]['text'][:12])]
print('C[0]:', C[0][:40])
print('C[-1]:', C[-1][:40])
print('prefix mismatch:', bad)

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
print('cand lens', clen)

with io.open(os.path.join(AD, 'out_009.json'), 'w', encoding='utf-8') as fh:
    fh.write(json.dumps(dict(map=res), ensure_ascii=False, separators=(',', ':')))
print('written out_009.json')
