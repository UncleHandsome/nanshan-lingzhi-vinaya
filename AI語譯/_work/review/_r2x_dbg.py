# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, '.')
import _r2a_lib as L

for r in L.parse_review(1778):
    print(r['seq'], r['seg'], len(r['trans'] or ''), (r['trans'] or '')[:12])
o = L.Out('03_業疏', '15a_卷三之四')
for seg in (70, 71, 72, 73):
    t = o.segs[seg - 1]
    print('SEG', seg, len(t), repr(t[:40]))
