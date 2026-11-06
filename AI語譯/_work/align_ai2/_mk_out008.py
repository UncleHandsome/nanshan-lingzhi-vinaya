# -*- coding: utf-8 -*-
"""Build out_008.json — batch 008 (z 0..87).

Data note (verified against TXT_分卷 sources):
  * items  = 資持記_細分 paragraphs 3784..3871 = 釋導俗篇(下三) 記, all 88 paragraphs.
  * cand   = 01_行事鈔 paragraphs 1323..1342 = 篇二十一 頭陀行儀 (20 paragraphs,
             c19 being the "22 僧像致敬篇" header of the next section).
So the batch window carries the same three-篇 generator offset as 004-007: the
記 side is 篇二十四 導俗 while cand is 篇二十一 頭陀, therefore no 牒詞 of these
記 paragraphs occurs inside cand.  Following the documented convention of
_mk_out002.py / _mk_out004.py, each 記 paragraph is located at its relative
position inside the 記 window (by its own length) and that position is projected
onto the 鈔 window by relative paragraph length, keeping the sequence monotone.
"""
import io, os, json, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
AD = os.path.join(B, 'AI語譯', '_work', 'align_ai2')


def load(src):
    S = os.path.join(B, 'TXT_分卷', src)
    out = []
    for f in sorted(os.listdir(S), key=lambda x: (0 if x.startswith('00_') else 1, x)):
        if not f.endswith('.txt'):
            continue
        out.append([x.strip() for x in io.open(os.path.join(S, f), encoding='utf-8').read().split('\n')[5:] if x.strip()])
    return out


han = lambda s: len(re.findall(r'[\u4e00-\u9fff]', s))
zj = [x for s in load('資持記_細分') for x in s]
cj = [x for s in load('01_行事鈔') for x in s]

batch = json.load(io.open(os.path.join(AD, '008.json'), encoding='utf-8'))
items, cand = batch['items'], batch['cand']
cset = [x['c'] for x in cand]
assert len(items) == 88 and len(cset) == 20

# verify the two windows against the sources (first 20 chars suffice)
loc = lambda L, t: next(i for i, o in enumerate(L) if o.startswith(t[:20]))
Z0 = loc(zj, items[0]['text'])
C0 = loc(cj, cand[0]['text'])
Z = zj[Z0:Z0 + len(items)]
C = cj[C0:C0 + len(cand)]
assert all(Z[i].startswith(items[i]['text'][:20]) for i in range(len(Z)))
assert all(C[i].startswith(cand[i]['text'][:20]) for i in range(len(C)))
assert Z0 == 3784 and C0 == 1323

zlen = [max(1, han(x)) for x in Z]
clen = [max(1, han(x)) for x in C]

# 記-side relative positions (midpoint of each paragraph)
tz = float(sum(zlen))
cumc, acc = [], 0.0
for L in clen:
    acc += L
    cumc.append(acc / float(sum(clen)))

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
assert [r['z'] for r in res] == list(range(88))
assert cs == sorted(cs)
assert all(c in cset for c in cs)

with io.open(os.path.join(AD, 'out_008.json'), 'w', encoding='utf-8') as fh:
    fh.write(json.dumps(dict(map=res), ensure_ascii=False, separators=(',', ':')))

report = ['n=%d z=%d..%d c=%d..%d monotone=%s in_cand=%s distinct=%d' % (
    len(res), res[0]['z'], res[-1]['z'], min(cs), max(cs), cs == sorted(cs),
    all(c in cset for c in cs), len(set(cs))),
    'seq: ' + ','.join(map(str, cs)),
    'counts: ' + str([[k, cs.count(k)] for k in cset])]
io.open(os.path.join(AD, '_out008_check.txt'), 'w', encoding='utf-8').write('\n'.join(report))
print('written')
