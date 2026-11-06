# -*- coding: utf-8 -*-
import json, io, os, re, difflib

base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
W = os.path.join(base, 'AI語譯', '_work')

def load_full(p):
    out = {}
    for line in io.open(p, encoding='utf-8'):
        line = line.strip()
        if not line:
            continue
        m = re.match(r'^\[([zc])(\d+)\]\s*(.*)$', line)
        if m:
            out[int(m.group(2))] = m.group(3)
    return out

fullz = load_full(os.path.join(W, 'align_fix', '_tmp029_ji_full.txt'))
fullc = load_full(os.path.join(W, 'align_fix', '_tmp029_cao_full.txt'))
print('fullz', len(fullz), min(fullz), max(fullz))
print('fullc', len(fullc), min(fullc), max(fullc))

data = json.load(io.open(os.path.join(W, 'align_fix2', '002.json'), encoding='utf-8'))
items = data['items']; cands = data['cand']
print('items', len(items), 'cands', len(cands))

# verify item text matches full text prefix
bad = 0
for it in items:
    z = it['z']
    ft = fullz.get(z)
    if ft is None or not ft.startswith(it['text'][:20]):
        bad += 1
        print('MISMATCH z', z, repr(it['text'][:30]), '||', repr((ft or '')[:30]))
print('prefix mismatch', bad)
print('lens fullz', [(z, len(fullz[z])) for z in sorted(fullz)][:5])

# check z47 not in items
print('z47 in items?', any(it['z'] == 47 for it in items))

# ---- character-level monotonic alignment of concatenated 記 onto 鈔 ----
cao = ''
cstart = {}
for c in sorted(fullc):
    cstart[c] = len(cao)
    cao += fullc[c]
print('cao len', len(cao))

zcat = ''
zstart = {}
for z in sorted(fullz):
    zstart[z] = len(zcat)
    zcat += fullz[z]
print('zcat len', len(zcat))

sm = difflib.SequenceMatcher(None, zcat, cao, autojunk=False)
blocks = [b for b in sm.get_matching_blocks() if b.size >= 2]
print('blocks', len(blocks), 'total matched chars', sum(b.size for b in blocks))

# map cao index -> c
import bisect
cids = sorted(fullc)
cposes = [cstart[c] for c in cids]
def c_of(pos):
    i = bisect.bisect_right(cposes, pos) - 1
    return cids[i]

rows = []
for it in items:
    z = it['z']
    s0 = zstart[z]; s1 = s0 + len(fullz[z])
    bs = [b for b in blocks if b.a >= s0 and b.a < s1]
    detail = ['%d(%d,%s)' % (c_of(b.b), b.size, fullc[c_of(b.b)][b.b - cstart[c_of(b.b)]: b.b - cstart[c_of(b.b)] + b.size][:12]) for b in bs]
    rows.append((z, s1 - s0, detail))

with io.open(os.path.join(os.path.dirname(__file__), '_a002_align.txt'), 'w', encoding='utf-8') as f:
    for z, ln, detail in rows:
        f.write('z%-2d len=%-3d  %s\n' % (z, ln, ' '.join(detail)))
print('written _a002_align.txt')
