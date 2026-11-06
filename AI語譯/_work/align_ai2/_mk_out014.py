# -*- coding: utf-8 -*-
"""Build out_014.json for align_ai2 batch 014.

Situation verified against the sources (TXT_分卷/資持記_細分, TXT_分卷/01_行事鈔):
  * items (53 paras) = the tail block of 資持記 下四: the 30 釋諸部篇 記
    (28 段落, 釋 鈔 篇三十 諸部別行) followed by the 校注 (校勘記) appendix
    (25 paragraphs, page-based variant readings); no 牒詞 test can match cand.
  * cand (48 paras) = 鈔 篇二十七 諸雜要行 (47 段落) + the next 篇 heading
    (沙彌別行篇), i.e. a three-篇 offset from the 記 window.
So the only consistent reading is a monotone projection:
  - the 28 記 paragraphs are laid out proportionally (by real hanzi length of
    the source paragraphs, not the 70-char previews) over c0..c46;
  - the 25 校注 paragraphs are 校勘記, not explanatory text, so they inherit the
    last body value c46 ("總科通釋沿用前一記段 c").
"""
import io
import os
import re
import json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
AD = os.path.join(B, 'AI語譯', '_work', 'align_ai2')
ZDIR = os.path.join(B, 'TXT_分卷', '資持記_細分')
CDIR = os.path.join(B, 'TXT_分卷', '01_行事鈔')
han = lambda s: ''.join(re.findall(r'[\u4e00-\u9fff]', s))


def load(d):
    out = []
    for f in sorted(os.listdir(d), key=lambda x: (0 if x.startswith('00_') else 1, x)):
        if not f.endswith('.txt'):
            continue
        sp = [x.strip() for x in io.open(os.path.join(d, f), encoding='utf-8').read().split('\n')[5:] if x.strip()]
        out += sp
    return out


Z = load(ZDIR)
S = load(CDIR)
batch = json.load(io.open(os.path.join(AD, '014.json'), encoding='utf-8'))
items, cand = batch['items'], batch['cand']
nz, nc = len(items), len(cand)
assert nz == 53 and nc == 48, (nz, nc)

iz = next(i for i, p in enumerate(Z) if p.startswith(items[0]['text'][:14]))
ic = next(i for i, p in enumerate(S) if p.startswith(cand[0]['text'][:14]))
Zp = Z[iz:iz + nz]
Cp = S[ic:ic + nc]
assert len(Zp) == nz and len(Cp) == nc

# preview sanity: every item/cand preview must be a prefix of the real paragraph
zbad = [i for i in range(nz) if not Zp[i].startswith(items[i]['text'][:30])]
cbad = [i for i in range(nc) if not Cp[i].startswith(cand[i]['text'][:30])]
print('z window', iz, '| cand window', ic)
print('preview mismatches: z', zbad, '| c', cbad)

cset = [x['c'] for x in cand]
assert cset == list(range(nc))

# 28 記 body paragraphs, 47 鈔 paragraphs of 篇二十七 (c47 = next 篇 heading)
NB = 28
body_last = nc - 2  # c46

zl = [max(1, len(han(Zp[i]))) for i in range(NB)]
cl = [max(1, len(han(Cp[j]))) for j in range(body_last + 1)]
tz = float(sum(zl))
tc = float(sum(cl))

cum_c, acc = [], 0.0
for L in cl:
    acc += L
    cum_c.append(acc / tc)

res, last, pos = [], 0, 0.0
for i in range(NB):
    mid = (pos + zl[i] / 2.0) / tz
    pos += zl[i]
    j = 0
    while j < len(cum_c) - 1 and cum_c[j] < mid:
        j += 1
    j = max(last, min(j, body_last))
    last = j
    res.append(dict(z=items[i]['z'], c=cset[j]))

for i in range(NB, nz):
    res.append(dict(z=items[i]['z'], c=cset[body_last]))

cs = [r['c'] for r in res]
assert len(res) == nz
assert all(cs[i] <= cs[i + 1] for i in range(len(cs) - 1))
assert all(c in cset for c in cs)

print('rows', len(res), '| z', res[0]['z'], '..', res[-1]['z'])
print('c seq', cs)
print('dist', {c: cs.count(c) for c in sorted(set(cs))})

io.open(os.path.join(AD, 'out_014.json'), 'w', encoding='utf-8').write(
    json.dumps(dict(map=res), ensure_ascii=False, separators=(',', ':')))
print('written out_014.json')
