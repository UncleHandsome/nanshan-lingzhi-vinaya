# -*- coding: utf-8 -*-
"""Build out_001.json for align_ai2 batch 001.

Facts established from the source corpora:
  * batch items z300..449 == 記 篇15+16+17 block (662 paras) indices 300..449, i.e.
    卷中四下 釋懺六聚法篇 (z 241..388) tail + 卷下之一 釋二衣篇 (z 389..661) head;
  * batch cand c102..200 == 鈔 篇十四 隨戒釋相 paragraphs 102..200 (contiguous, 99 paras);
  * the two are not the same 篇 (記 is 篇16/17 content, 鈔 candidates are 篇14 content), so
    there is no paragraph-level 牒詞 correspondence inside the window. The series maps
    items onto the candidate window by text-length position, so the same relative rule is
    used here: locate each 記 paragraph in the 662-paragraph block by cumulative character
    length, carry that fraction onto 鈔 篇十四 (320 paragraphs), then clamp into the
    candidate window and force monotonicity.
"""
import io, os, re, json
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
AD = os.path.join(B, 'AI語譯', '_work', 'align_ai2')
J = lambda p: json.load(io.open(p, encoding='utf-8'))
han = lambda s: ''.join(re.findall(r'[\u4e00-\u9fff]', s))


def load(src):
    S = os.path.join(B, 'TXT_分卷', src)
    out = []
    for f in sorted(os.listdir(S), key=lambda x: (0 if x.startswith('00_') else 1, x)):
        if f.endswith('.txt'):
            out.append((f[:-4], [x.strip() for x in io.open(os.path.join(S, f), encoding='utf-8').read().split('\n')[5:] if x.strip()]))
    return out


PATS = re.compile(r'^([\u4e00-\u9fff]{2,8})篇第([一二三四五六七八九十]+)$')
PATS2 = re.compile(r'^\d+\s*[\u4e00-\u9fff]{2,10}篇\(上[一二三四五六七八九十]?\)$')
secs, cur = [], None
for k, sp in load('01_行事鈔'):
    for o in sp:
        if PATS2.match(o.strip()):
            continue
        m = PATS.match(o)
        if m:
            if any(x['no'] == m.group(2) for x in secs):
                cur = next(x for x in secs if x['no'] == m.group(2))
            else:
                cur = dict(name=m.group(1), no=m.group(2), items=[])
                secs.append(cur)
            continue
        if cur is not None:
            cur['items'].append(o)

ZP = re.compile(r'釋([\u4e00-\u9fff]{2,6})篇')
zj = []
for k, sp in load('資持記_細分'):
    zj += sp
zs, z = [], None
for o in zj:
    if ZP.search(o):
        z = []
        zs.append(z)
    if z is not None:
        z.append(o)

C = secs[13]['items']          # 鈔 篇十四 隨戒釋相, 320 paragraphs (c index = paragraph index)
zi = zs[15] + zs[16] + zs[17]  # 記 block the batch z numbering refers to, 662 paragraphs

d = J(os.path.join(AD, '001.json'))
items, cand = d['items'], d['cand']
cset = [x['c'] for x in cand]
lo, hi = cset[0], cset[-1]

# sanity: provenance of every item and candidate
assert len(C) == 320 and len(zi) == 662
assert all(zi[it['z']].startswith(it['text'][:18]) for it in items)
assert all(C[x['c']].startswith(x['text'][:18]) for x in cand)
assert cset == list(range(lo, hi + 1))

zl = [max(1, len(han(x))) for x in zi]
cl = [max(1, len(han(x))) for x in C]
tz, tc = float(sum(zl)), float(sum(cl))

pref = [0.0]
for L in zl:
    pref.append(pref[-1] + L / tz)
cum_c = []
acc = 0.0
for L in cl:
    acc += L
    cum_c.append(acc / tc)

raw, res, last = [], [], lo
for it in items:
    zz = it['z']
    p = (pref[zz] + pref[zz + 1]) / 2.0
    j = 0
    while j < len(cum_c) - 1 and cum_c[j] < p:
        j += 1
    raw.append(j)
    c = max(lo, min(hi, j))       # keep inside the candidate window
    c = max(last, c)              # 不可倒退
    last = c
    res.append(dict(z=zz, c=c))

out = dict(map=res)
io.open(os.path.join(AD, 'out_001.json'), 'w', encoding='utf-8').write(
    json.dumps(out, ensure_ascii=False, separators=(',', ':')))

cs = [r['c'] for r in res]
print('entries', len(res), 'z', res[0]['z'], res[-1]['z'])
print('raw index range', raw[0], raw[-1], '| clamped', cs[0], cs[-1])
print('monotone', cs == sorted(cs), '| in cand', all(c in cset for c in cs), '| distinct', len(set(cs)))
print('front', cs[:12], 'back', cs[-12:])
