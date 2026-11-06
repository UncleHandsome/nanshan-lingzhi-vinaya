# -*- coding: utf-8 -*-
import io, os, re, json, importlib.util, sys
sys.stdout.reconfigure(encoding='utf-8')
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
D = os.path.join(B, 'AI語譯', '_work', 'align_fix')
spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)
SECS = ex.sections(); ZS = ex.zsecs()
SKIP1 = re.compile(r'^\d+\s*[\u4e00-\u9fff]{2,10}篇\(上[一二三四五六七八九十]?\)$')
SKIP2 = re.compile(r'^[\u4e00-\u9fff]{2,10}篇第[一二三四五六七八九十]+$')
idx = 17
C = [o for o, t in SECS[idx]['items'] if not SKIP1.match(o.strip()) and not SKIP2.match(o.strip())]
Z = ex.zitems_for(idx, ZS)
print('sec', SECS[idx]['name'], 'C', len(C), 'Z', len(Z))
with io.open(os.path.join(D, '_t020_ji.txt'), 'w', encoding='utf-8') as f:
    for z in range(len(Z)):
        f.write('[z%d] %s\n\n' % (z, Z[z][0]))
with io.open(os.path.join(D, '_t020_cao.txt'), 'w', encoding='utf-8') as f:
    for c in range(len(C)):
        f.write('[c%d] %s\n\n' % (c, C[c]))
J = json.load(io.open(os.path.join(D, '020.json'), encoding='utf-8'))
print('items', len(J['items']), 'cand', len(J['cand']))
bad=0
for it in J['items']:
    if not Z[it['z']][0].startswith(it['text'][:40]):
        bad+=1; print('MISMATCH z', it['z'], repr(it['text'][:25]), '||', repr(Z[it['z']][0][:25]))
for cd in J['cand']:
    if not C[cd['c']].startswith(cd['text'][:40]):
        bad+=1; print('MISMATCH c', cd['c'], repr(cd['text'][:25]), '||', repr(C[cd['c']][:25]))
print('mismatches', bad)
AM = json.load(io.open(os.path.join(B, 'AI語譯', '_work', 'hb_align.json'), encoding='utf-8'))
a = AM.get(str(idx))
print('hb_align len', len(a) if a else None)
if a: print('hb', a)
