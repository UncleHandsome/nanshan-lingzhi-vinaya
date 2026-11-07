# -*- coding: utf-8 -*-
import io, os, re, json

REV = os.path.dirname(os.path.abspath(__file__))
res = json.load(io.open(os.path.join(REV, '_g1b_sel.json'), encoding='utf-8'))

def quotes(s):
    out = []
    for m in re.finditer(r'「([^」]{2,200})」', s):
        out.append(m.group(1))
    for m in re.finditer(r'『([^』]{2,200})』', s):
        out.append(m.group(1))
    return out

w = io.open(os.path.join(REV, '_g1b_qcheck.txt'), 'w', encoding='utf-8')
for i, x in enumerate(res, 1):
    cur = x['out_para'] or ''
    hits, miss = [], []
    for q in quotes(x['problem']) + quotes(x['suggestion']):
        if len(q) < 6:
            continue
        (hits if q in cur else miss).append(q)
    w.write('%2d %-12s seg=%-4s hits=%d miss=%d\n' % (i, x['chunk'], x['seg'], len(hits), len(miss)))
    for h in hits:
        w.write('    HIT  %s\n' % h)
    for m in miss:
        w.write('    MISS %s\n' % m)
w.close()
print('ok')
