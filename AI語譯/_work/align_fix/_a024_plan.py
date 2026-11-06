#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
hb = json.load(open(os.path.join(HERE, '_a024_hb.json'), encoding='utf-8'))
J = [t.replace('【記】', '').strip() for k, t in hb if k == 'J']
C = [t.replace('【鈔】', '').strip() for k, t in hb if k == 'C']
m = [0]*6 + [3]*8 + [4]*3 + [5] + [6]*11 + [7]*15 + [8]*2 + [9]*7 + [11]*14 + [12]*12 + [13]*6 + [14]*7
assert len(m) == 92, len(m)
lines = []
lines.append('=== CAND (c : head) ===')
for i, c in enumerate(C):
    lines.append(f'c{i-1:2d} [{len(c):4d}] {c[:60]}')
lines.append('')
lines.append('=== ITEMS (z -> c : head) ===')
for z, j in enumerate(J):
    lines.append(f'z{z:2d} -> c{m[z]:2d} [{len(j):3d}] {j[:60]}')
open(os.path.join(HERE, '_a024_plan.txt'), 'w', encoding='utf-8').write('\n'.join(lines))
print('written', len(J))
