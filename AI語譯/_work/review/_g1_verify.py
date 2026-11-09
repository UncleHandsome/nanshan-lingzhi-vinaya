# -*- coding: utf-8 -*-
import json, re

ns = {}
exec(open('AI語譯/_work/review/_g1_build.py', encoding='utf-8').read(), ns)
D = ns['D']
M = ns['M']
NP_EDITS = ns['NP_EDITS']
out = {('02_戒疏', ch, sg): t for b, ch, sg, t in ns['out_rows']}

missing = []
for r in D:
    gid = r['gid']
    if gid in M:
        ops = M[gid]
        src = 'manual'
    elif gid in NP_EDITS:
        ops = NP_EDITS[gid]
        src = 'np'
    elif r['status'] == 'auto':
        ops = [('rep', p[0][0], ns['deq'](ns['strip_alt'](p[1]))) for p in r['pairs']]
        src = 'auto'
    else:
        continue
    t = out.get(('02_戒疏', r['chunk'], r['seg']))
    if t is None:
        continue
    for op in ops:
        new = op[2]
        if new == '【疏文】':
            continue
        if new not in t:
            # maybe the row was a duplicate and edit was different -> report
            missing.append((gid, src, new[:40], r['chunk'], r['seg']))

print('missing', len(missing))
for m in missing:
    print(m)
