# -*- coding: utf-8 -*-
import io, os, re, json, importlib.util, sys

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
sys.stdout.reconfigure(encoding='utf-8')
spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)
SECS = ex.sections(); ZS = ex.zsecs()
print('secs', len(SECS), 'zs', len(ZS))
print('Z2S', ex.Z2S)
zsec_names = [(i, s['name'], len(s['items'])) for i, s in enumerate(ZS)]
print(zsec_names)
print('sec27', len(SECS[27]['items']), SECS[27]['name'])
Z = ex.zitems_for(27, ZS)
print('Z for 27:', len(Z))
AM = json.load(io.open(os.path.join(B, 'AI語譯', '_work', 'hb_align.json'), encoding='utf-8'))
am = AM['27']
print('am len', len(am), 'monotone', all(am[i] <= am[i+1] for i in range(len(am)-1)), 'range', min(am), max(am))

data = json.load(io.open(os.path.join(B, 'AI語譯', '_work', 'align_fix2', '002.json'), encoding='utf-8'))
items = data['items']

# map chunks to sentence indices by text search over concatenated Z text
zcat = ''
zpos = []
for i, (o, t) in enumerate(Z):
    zpos.append(len(zcat))
    zcat += o
print('zcat len', len(zcat))

out = []
out.append('==== Z sentences for sec27 (n=%d) with hb c ====' % len(Z))
for i, (o, t) in enumerate(Z):
    c = am[i] if i < len(am) else None
    out.append('S%-2d [c%-2s] len=%-3d %s' % (i, c, len(o), o[:80]))
out.append('')
out.append('==== chunk starts ====')
import bisect
starts = []
for it in items:
    t = it['text']
    k = zcat.find(t[:20])
    if k < 0:
        k = zcat.find(t[:12])
    starts.append(k)
    # find sentence index containing k
    si = bisect.bisect_right(zpos, k) - 1 if k >= 0 else -1
    out.append('z%-2d pos=%-5s sent=%-3s c=%s' % (it['z'], k, si, (am[si] if si >= 0 else None)))

io.open(os.path.join(B, 'AI語譯', '_work', 'align_fix2', '_a002_hb27.txt'), 'w', encoding='utf-8').write('\n'.join(out))
print('written')
