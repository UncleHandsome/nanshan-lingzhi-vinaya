# -*- coding: utf-8 -*-
"""Build out_022.json for section 20 (對施興治)."""
import io, json, os, sys
sys.stdout.reconfigure(encoding='utf-8')
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\align_fix'
J = json.load(io.open(os.path.join(D, '022.json'), encoding='utf-8'))
n = len(J['items'])
cs = [0]*9 + [1]*3 + [2]*4 + [3]*2 + [4]*9 + [5]*8
assert len(cs) == n, (len(cs), n)
assert all(a <= b for a, b in zip(cs, cs[1:]))
assert all(0 <= c < len(J['cand']) for c in cs)
mp = {'map': [{'z': i, 'c': c} for i, c in enumerate(cs)]}
with io.open(os.path.join(D, 'out_022.json'), 'w', encoding='utf-8', newline='\n') as f:
    f.write(json.dumps(mp, ensure_ascii=False, separators=(',', ':')))
print('written', len(cs), 'items; c runs:', cs[0], cs[9], cs[12], cs[16], cs[18], cs[27])
