# -*- coding: utf-8 -*-
"""比對 校閱 material 譯文 與 現行 out 同段，統計差異（找出已被先前批次改過的段）。"""
import os, sys, json, difflib
sys.path.insert(0, os.path.dirname(__file__))
import _r2a_lib as L

n0, n1 = int(sys.argv[1]), int(sys.argv[2])
only = sys.argv[3] if len(sys.argv) > 3 else None
tot = same = diff = miss = 0
out = []
cache = {}
for n in range(n0, n1 + 1):
    for r in L.parse_review(n):
        key = (r['book'], r['chunk'])
        if key not in cache:
            try:
                cache[key] = L.Out(*key)
            except Exception:
                cache[key] = None
        o = cache[key]
        tot += 1
        if o is None or r['seg'] - 1 >= len(o.segs):
            miss += 1
            out.append((n, r['seq'], r['book'], r['chunk'], r['seg'], 'MISSING', '', ''))
            continue
        cur = o.segs[r['seg'] - 1]
        mat = (r['trans'] or '').replace('\n', '')
        if cur.replace('\n', '') == mat:
            same += 1
        else:
            diff += 1
            if only and only != r['chunk']:
                continue
            sm = difflib.SequenceMatcher(None, mat, cur)
            ops = []
            for tag, i1, i2, j1, j2 in sm.get_opcodes():
                if tag != 'equal':
                    ops.append('%s:%r=>%r' % (tag, mat[i1:i2][:40], cur[j1:j2][:40]))
            out.append((n, r['seq'], r['book'], r['chunk'], r['seg'], 'DIFF', len(ops), ' | '.join(ops[:4])))
print('total %d same %d diff %d missing %d' % (tot, same, diff, miss))
w = 0
for row in out:
    if row[5] == 'MISSING':
        print('MISS', row)
        continue
    if w < 40:
        print(row[0], row[1], row[3], row[4], row[5], row[6])
        print('   ', row[7][:600])
        w += 1
print('...diff total', diff)
