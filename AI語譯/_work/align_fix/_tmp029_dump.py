# -*- coding: utf-8 -*-
import json, os, io

base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

def read_lines(p):
    with io.open(p, encoding='utf-8') as f:
        return [l.rstrip('\n').rstrip('\r') for l in f]

cao = []
for name, lo, hi in [('12a_卷下之四.txt', 33, 10**9), ('12b_卷下之四.txt', 6, 16)]:
    p = os.path.join(base, 'TXT_分卷', '01_行事鈔', name)
    lines = read_lines(p)
    for ln in range(lo, min(hi, len(lines)) + 1):
        s = lines[ln - 1].strip().strip('\u3000').strip()
        if s:
            cao.append((name, ln, s))

out2 = []
for i, (n, ln, s) in enumerate(cao):
    out2.append('[c%d] %s' % (i, s))
io.open(os.path.join(os.path.dirname(__file__), '_tmp029_cao_full.txt'), 'w', encoding='utf-8').write('\n\n'.join(out2))

ji = []
for name, lo, hi in [('16a_下四.txt', 47, 10**9), ('16b_下四.txt', 6, 30)]:
    p = os.path.join(base, 'TXT_分卷', '資持記_細分', name)
    lines = read_lines(p)
    for ln in range(lo, min(hi, len(lines)) + 1):
        s = lines[ln - 1].strip()
        if s:
            ji.append((name, ln, s))
out3 = []
for i, (n, ln, s) in enumerate(ji):
    out3.append('[z%d] %s' % (i, s))
io.open(os.path.join(os.path.dirname(__file__), '_tmp029_ji_full.txt'), 'w', encoding='utf-8').write('\n\n'.join(out3))
print('cao', len(cao), 'ji', len(ji))
