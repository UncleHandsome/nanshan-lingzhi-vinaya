# -*- coding: utf-8 -*-
"""Review dump: each 記 z with assigned 鈔 c, flagging jumps."""
import io, os, json, re, importlib.util, sys
sys.stdout.reconfigure(encoding='utf-8')
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
D = os.path.join(B, 'AI語譯', '_work', 'align_fix')
spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)
SECS = ex.sections(); ZS = ex.zsecs()
Z = [o for o, t in ex.zitems_for(15, ZS)]
C = [o for o, t in SECS[15]['items']]
o = json.load(io.open(os.path.join(D, 'out_017.json'), encoding='utf-8'))['map']
lines = []
prev = None
for m in o:
    z, c = m['z'], m['c']
    mark = ''
    if prev is not None and c - prev >= 2:
        mark = '  <<< jump +%d' % (c - prev)
    prev = c
    lines.append('z%-3d c%-3d | 記:%s' % (z, c, Z[z][:34]))
    lines.append('           | 鈔:%s%s' % (C[c][:56], mark))
io.open(os.path.join(D, '_a017_review.txt'), 'w', encoding='utf-8').write('\n'.join(lines))
print('ok', len(o))
