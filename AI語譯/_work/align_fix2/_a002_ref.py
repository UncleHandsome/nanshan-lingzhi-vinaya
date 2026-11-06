# -*- coding: utf-8 -*-
import io, os, re, json, importlib.util, sys

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
sys.stdout.reconfigure(encoding='utf-8')
spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)
SECS = ex.sections(); ZS = ex.zsecs()
AM = json.load(io.open(os.path.join(B, 'AI語譯', '_work', 'hb_align.json'), encoding='utf-8'))

out = []
# show section idx 27 (沙彌) alignment: first 25 ji sentences with c, and the cao paragraphs
for idx in [27]:
    C = SECS[idx]['items']
    Z = ex.zitems_for(idx, ZS)
    am = AM.get(str(idx), [])
    out.append('#### idx %d %s  C=%d Z=%d am=%d' % (idx, SECS[idx]['name'], len(C), len(Z), len(am)))
    for i, (o, t) in enumerate(C[:12]):
        out.append('[c%-2d] %s' % (i, o[:70]))
    out.append('')
    for i, (o, t) in enumerate(Z[:40]):
        c = am[i] if i < len(am) else None
        out.append('S%-2d -> c%-2s | %s' % (i, c, o[:70]))

io.open(os.path.join(B, 'AI語譯', '_work', 'align_fix2', '_a002_ref.txt'), 'w', encoding='utf-8').write('\n'.join(out))
print('ok')
