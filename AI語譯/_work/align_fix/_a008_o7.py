# -*- coding: utf-8 -*-
import io, os, sys, json
sys.stdout.reconfigure(encoding='utf-8')
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
D = os.path.join(B, 'AI語譯', '_work', 'align_fix')
o7 = json.load(io.open(os.path.join(D, 'out_007.json'), encoding='utf-8'))['map']
m7 = {int(x['z']): int(x['c']) for x in o7}
prev = None
for z in sorted(m7):
    if m7[z] != prev:
        print('z=%d -> c=%d' % (z, m7[z]))
        prev = m7[z]
d = json.load(io.open(os.path.join(D, '_a008_data.json'), encoding='utf-8'))
J = d['ji']
for z in [150, 165, 174, 179, 190, 204, 207, 218, 260, 264, 270, 280, 290, 295, 298, 299]:
    print('\n=== 記 z=%d ===\n%s' % (z, J[z]))
