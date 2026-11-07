# -*- coding: utf-8 -*-
import io, os
REV = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(REV, 'located_all.tsv')
lines = io.open(SRC, encoding='utf-8').read().split('\n')
hdr = lines[0].split('\t')
w = io.open(os.path.join(REV, '_g1b_diffrows.txt'), 'w', encoding='utf-8')
n = 0
for line in lines[1:]:
    if not line.strip():
        continue
    f = line.split('\t')
    if len(f) != len(hdr):
        continue
    d = dict(zip(hdr, f))
    if d['orig'] != d['current'] and d['book']:
        n += 1
        w.write('%s | %s | seg=%s | votes=%s\nORIG: %s\nCURR: %s\n\n' % (d['book'], d['chunk'], d['seg'], d['votes'], d['orig'][:300], d['current'][:300]))
w.close()
print('diff rows with book:', n)
