# -*- coding: utf-8 -*-
"""Build out_010.json: map the 41 記 segments (z 0..40) of batch 010 to 鈔 candidates c.

Data note (verified against the sources):
  * items = 資持記_細分 paragraphs of 釋瞻病篇 (下四, 記 篇二十六), 41 paragraphs.
  * cand  = 行事鈔 篇二十三 訃請設則 (12 段, c 0..11, c=11 being the
    「24 導俗化方篇」 header).
So this batch pairs the 記 of 篇二十六 瞻病 with the 鈔 of 篇二十三 訃請設則
(the same three-篇 offset that affects batches 004-014), and no 牒詞 of the 記
finds its 鈔 phrase inside cand.

Convention used for such offset windows (see _mk_out002.py / _mk_out004.py):
locate each 記 paragraph inside its own 記 window, project that relative
(character-length) position onto the candidate window, keep the sequence
monotone, and only emit c values that exist in cand.
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
        out += sp
    return out


batch = json.load(io.open(os.path.join(AD, '010.json'), encoding='utf-8'))
items, cand = batch['items'], batch['cand']
cset = [x['c'] for x in cand]
assert len(items) == 41 and len(cset) == 12, (len(items), len(cset))

# --- 記 window: 釋瞻病篇 (下四) ---
Z = load('資持記_細分')
i0 = next(i for i, p in enumerate(Z) if p.startswith('四分律行事鈔資持記下四2') and '釋瞻病篇' in p[:40])
Zp = Z[i0:i0 + len(items)]
assert len(Zp) == len(items)
prefix_ok = sum(1 for j, p in enumerate(Zp) if p.startswith(items[j]['text'][:20]))
print('記 window at', i0, '| prefix match', prefix_ok, '/', len(Zp))

# --- 鈔 window: 訃請設則 ---
S = load('01_行事鈔')
s0 = next(i for i, p in enumerate(S) if p.startswith('夫昏俗多務'))
C = S[s0:s0 + len(cand)]
assert len(C) == len(cand)
c_ok = sum(1 for j, p in enumerate(C) if p.startswith(cand[j]['text'][:12]))
print('鈔 window at', s0, '| prefix match', c_ok, '/', len(C))

# lengths from the real sources (cand/items text is truncated to 70 chars)
zlen = [max(1, len(p)) for p in Zp]
clen = [max(1, len(p)) for p in C]
tz = float(sum(zlen))
tc = float(sum(clen))

cumc, acc = [], 0.0
for L in clen:
    acc += L
    cumc.append(acc / tc)

res, last, pos = [], 0, 0.0
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
assert len(res) == len(items)
assert cs == sorted(cs)
assert all(c in cset for c in cs)
print('items', len(res), '| z', res[0]['z'], '..', res[-1]['z'])
print('c', cs[0], '..', cs[-1], '| distinct', len(set(cs)))
print('seq', cs)

with io.open(os.path.join(AD, 'out_010.json'), 'w', encoding='utf-8') as fh:
    fh.write(json.dumps(dict(map=res), ensure_ascii=False, separators=(',', ':')))
print('written out_010.json')
