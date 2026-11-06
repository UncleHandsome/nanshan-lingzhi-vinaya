# -*- coding: utf-8 -*-
"""Verify: batch 001 items live in 記 篇15+16+17 block (662 paras); cand = 鈔 篇14 (320 paras)."""
import io, os, re, json
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
AD = os.path.join(B, 'AI語譯', '_work', 'align_ai2')
J = lambda p: json.load(io.open(p, encoding='utf-8'))


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

log = []
log.append('記 sections: ' + ', '.join('%d:%d' % (i, len(x)) for i, x in enumerate(zs)))
C = secs[13]['items']
zi = zs[15] + zs[16] + zs[17]
log.append('C(篇%s %s) n=%d ; zi n=%d' % (secs[13]['no'], secs[13]['name'], len(C), len(zi)))
log.append('C[0]=%s' % C[0][:40])
log.append('C[102]=%s' % C[102][:40])
log.append('C[200]=%s' % C[200][:40])
log.append('C[319]=%s' % C[319][:40])
log.append('zi[300]=%s' % zi[300][:40])
log.append('zi[388]=%s' % zi[388][:40])
log.append('zi[389]=%s' % zi[389][:40])
log.append('zi[661]=%s' % zi[661][:40])

d = J(os.path.join(AD, '001.json'))
items, cand = d['items'], d['cand']
cset = [x['c'] for x in cand]
log.append('cand contiguous: %s (%d..%d, n=%d)' % (cset == list(range(cset[0], cset[-1] + 1)), cset[0], cset[-1], len(cset)))
bad = [it['z'] for it in items if not zi[it['z']].startswith(it['text'][:18])]
log.append('items mismatched vs zi: %d %s' % (len(bad), bad[:5]))
badc = [x['c'] for x in cand if not C[x['c']].startswith(x['text'][:18])]
log.append('cand mismatched vs C: %d %s' % (len(badc), badc[:5]))
io.open(os.path.join(AD, '_verify.txt'), 'w', encoding='utf-8').write('\n'.join(log))
print('\n'.join(log))
