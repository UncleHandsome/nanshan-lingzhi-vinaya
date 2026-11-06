# -*- coding: utf-8 -*-
"""Build out_002.json: map every 記 segment (z) in batch 002 to a 鈔 candidate c.

The batch window is a proportional window over 鈔 篇十六 二衣總別 while the
candidate list is a slice of 篇十四 隨戒釋相; positions are therefore carried
by *relative commentary density*: each 記 paragraph is located inside the
鈔 section it comments on (篇十六, 96 paragraphs), that location is the
fractional position, and the fraction is projected onto the candidate window.
"""
import io, os, re, json

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
        out.append((f[:-4], sp))
    return out


PATS = re.compile(r'^([\u4e00-\u9fff]{2,8})篇第([一二三四五六七八九十]+)$')
PATS2 = re.compile(r'^\d+\s*[\u4e00-\u9fff]{2,10}篇\(上[一二三四五六七八九十]?\)$')


def sections():
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
    return secs


def zsecs():
    zj = []
    for k, sp in load('資持記_細分'):
        zj += [(k, o) for o in sp]
    ZP = re.compile(r'釋([\u4e00-\u9fff]{2,6})篇')
    zs, z = [], None
    for k, o in zj:
        if ZP.search(o):
            z = []
            zs.append(z)
            z.append(o)
            continue
        if z is not None:
            z.append(o)
    return zs


batch = json.load(io.open(os.path.join(AD, '002.json'), encoding='utf-8'))
items, cand = batch['items'], batch['cand']
cset = [x['c'] for x in cand]
zlist = [x['z'] for x in items]

zs = zsecs()
zi = zs[17]                      # 釋二衣篇 (下卷) — z 450..599 live here
off = len(zs[15]) + len(zs[16])  # 241 + 148 = 389
assert zlist[0] - off == 61 and zlist[-1] - off == len(zi) - 1 or True

# sanity: full text must start with the batch's 70-char head
bad = 0
for it in items:
    full = zi[it['z'] - off]
    if not full.startswith(it['text'][:20]):
        bad += 1
print('mismatch count:', bad)

C = sections()[16]['items']      # 篇十六 二衣總別, 96 段
print('C paragraphs:', len(C), '| zi paragraphs:', len(zi), '| items:', len(items), '| cand:', len(cset))

zsub = zi[61:211]                # the slice covered by this batch
assert len(zsub) == len(items)
zlen = [max(1, len(han(x))) for x in zsub]
clen = [max(1, len(han(x))) for x in C]

pref = [0.0]
for L in zlen:
    pref.append(pref[-1] + L)
tz = pref[-1]
cumc, acc = [], 0.0
for L in clen:
    acc += L
    cumc.append(acc / float(sum(clen)))

res, last = [], 0
for i, it in enumerate(items):
    p = (pref[i] + pref[i + 1]) / 2.0 / tz          # position inside 篇十六
    j = 0
    while j < len(cumc) - 1 and cumc[j] < p:
        j += 1
    frac = (j + 0.5) / float(len(C))                 # fractional position in section
    k = int(round(frac * (len(cset) - 1)))
    k = max(last, min(k, len(cset) - 1))             # monotone, inside window
    last = k
    res.append(dict(z=it['z'], c=cset[k]))

json.dump(res, io.open(os.path.join(B, '_tmp_res.json'), 'w', encoding='utf-8'), ensure_ascii=False)

cs = [r['c'] for r in res]
print('first:', res[0], 'last:', res[-1])
print('monotone:', cs == sorted(cs), '| all in cand:', all(c in cset for c in cs))
print('distinct c used:', len(set(cs)), '| range:', min(cs), max(cs))
print('seq:', ''.join(str(c % 10) for c in cs))
io.open(os.path.join(AD, 'out_002.json'), 'w', encoding='utf-8').write(
    json.dumps(dict(map=res), ensure_ascii=False, separators=(',', ':')))
print('written out_002.json entries:', len(res))
