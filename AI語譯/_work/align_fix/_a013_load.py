# -*- coding: utf-8 -*-
"""Load sec 14 data (batch 013: z 1050-1199) and dump full Z/C texts for alignment."""
import io, os, re, json, importlib.util, sys
sys.stdout.reconfigure(encoding='utf-8')

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
AD = os.path.join(B, 'AI語譯', '_work', 'align_fix')

spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ex)
SECS, ZS = ex.sections(), ex.zsecs()
SKIP1 = re.compile(r'^\d+\s*[\u4e00-\u9fff]{2,10}篇\(上[一二三四五六七八九十]?\)$')
SKIP2 = re.compile(r'^[\u4e00-\u9fff]{2,10}篇第[一二三四五六七八九十]+$')

IDX = 13
C = [o for o, t in SECS[IDX]['items'] if not SKIP1.match(o.strip()) and not SKIP2.match(o.strip())]
Z = ex.zitems_for(IDX, ZS)
J = json.load(io.open(os.path.join(AD, '013.json'), encoding='utf-8'))

print('sec', SECS[IDX]['name'], 'no', SECS[IDX]['no'])
print('len C', len(C), 'len Z', len(Z), 'cand', len(J['cand']), 'items', len(J['items']))
print('cand text match:', [c['text'] for c in J['cand']] == [o[:90] for o in C])
print('item z range', J['items'][0]['z'], J['items'][-1]['z'])
print('item text match:', [it['text'] for it in J['items']] == [o[:90] for o, t in Z[1050:1200]])
print('item count ok:', len(J['items']) == len(Z[1050:1200]))

with io.open(os.path.join(AD, '_a013_Z.txt'), 'w', encoding='utf-8') as f:
    for i, (o, t) in enumerate(Z, 0):
        if 1040 <= i <= 1204:
            f.write('[z%d] len=%d\n%s\n\n' % (i, len(o), o))

with io.open(os.path.join(AD, '_a013_C.txt'), 'w', encoding='utf-8') as f:
    for c, o in enumerate(C):
        f.write('[c%d] len=%d\n%s\n\n' % (c, len(o), o))
print('dumped')
