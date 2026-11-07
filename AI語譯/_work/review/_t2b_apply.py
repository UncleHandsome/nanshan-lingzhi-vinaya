# -*- coding: utf-8 -*-
import csv, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _t2b_ops import OPS, APPEND, CUT_FROM, PREPEND, APPEND50
import _t2b_tool as T

BASE = os.path.dirname(os.path.abspath(__file__))
na = T.load()
new = [None] * len(na)
errs = []

for i, r in enumerate(na):
    new[i] = r['current'].strip('\r\n')

for (i, old, rep) in OPS:
    cur = new[i]
    cnt = cur.count(old)
    if cnt != 1:
        errs.append('idx %d: old occurs %d times: %r' % (i, cnt, old[:40]))
        continue
    new[i] = cur.replace(old, rep)

for i, s in APPEND.items():
    new[i] = new[i] + s

for i, marker in CUT_FROM.items():
    pos = new[i].find(marker)
    if pos < 0:
        errs.append('idx %d: cut marker not found' % i)
    else:
        new[i] = new[i][:pos]

for i, s in PREPEND.items():
    new[i] = s + new[i]

new[50] = new[50] + APPEND50

# sanity: no change rows
unchanged = [i for i in range(len(na)) if new[i] == na[i]['current']]
if unchanged:
    errs.append('unchanged rows: %s' % unchanged)

# sanity: no newline / tab
for i, t in enumerate(new):
    if '\n' in t or '\r' in t or '\t' in t:
        errs.append('idx %d: control char' % i)
    if not t.strip():
        errs.append('idx %d: empty' % i)

if errs:
    print('ERRORS:')
    for e in errs:
        print(' ', e)
    sys.exit(1)

out = os.path.join(BASE, 'fix_t2b.tsv')
with open(out, 'w', encoding='utf-8', newline='') as f:
    for i, r in enumerate(na):
        f.write('%s\t%s\t%s\t%s\n' % (r['book'], r['chunk'], r['seg'], new[i]))
print('wrote', out, len(na), 'rows')

# verification dump
buf = []
for i, r in enumerate(na):
    buf.append('=== %d | %s | %s | %s ===' % (i, r['book'], r['chunk'], r['seg']))
    buf.append('OLD: ' + r['current'])
    buf.append('NEW: ' + new[i])
    buf.append('')
open(os.path.join(BASE, '_verify.txt'), 'w', encoding='utf-8').write('\n'.join(buf))
print('wrote _verify.txt')
