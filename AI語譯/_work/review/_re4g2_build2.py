# -*- coding: utf-8 -*-
import json, re

rows = json.load(open(r'AI語譯/_work/review/_re4g2_rows.json', encoding='utf-8'))
plan = {p['n']: p for p in json.load(open(r'AI語譯/_work/review/_re4g2_plan.json', encoding='utf-8'))}

import importlib.util
spec = importlib.util.spec_from_file_location('rules', r'AI語譯/_work/review/_re4g2_rules.py')
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
MAN = {k: [(o, n) for o, n in v] for k, v in R.MAN.items()}
B_FIX = dict(R.B_FIX)
SKIP_APPLIED = {11, 62, 68, 112}

# pass 1: compute per-row edit lists (old, new) with None for append
edits_by_key = {}
row_order = []   # (key, n)
skipped = []
problems = []
for d in rows:
    n = d['_n']; cur = d['current']
    key = (d['book'], d['chunk'], d['seg'])
    p = plan[n]
    if p['kind'] == 'NOSUG':
        skipped.append((n, 'nosug')); continue
    if n in SKIP_APPLIED:
        skipped.append((n, 'applied')); continue
    if p['kind'] == 'REPL_OK':
        a = p['a']; b = B_FIX.get(str(n), B_FIX.get(n, p['b']))
        if cur.count(a) != 1:
            problems.append((n, 'count', cur.count(a))); skipped.append((n, 'badrep')); continue
        ed = [(a, b)]
    elif n in MAN:
        ed = MAN[n]
        ok = True
        for old, rep in ed:
            if old is not None and cur.count(old) != 1:
                problems.append((n, 'man', old[:15])); ok = False
        if not ok:
            skipped.append((n, 'badman')); continue
    else:
        problems.append((n, 'norule')); skipped.append((n, 'norule')); continue
    edits_by_key.setdefault(key, {})[n] = ed
    row_order.append((key, n))

# pass 2: apply all edits per key to that key's current (report rows sharing seg have same current)
curmap = {}
for d in rows:
    curmap[(d['book'], d['chunk'], d['seg'])] = d['current']

newmap = {}
for key, edmap in edits_by_key.items():
    text = curmap[key]
    for n in sorted(edmap):
        for old, rep in edmap[n]:
            if old is None:
                text = text + rep
            else:
                if text.count(old) != 1:
                    problems.append((n, 'conflict', old[:15]))
                else:
                    text = text.replace(old, rep, 1)
    newmap[key] = text

# pass 3: emit one line per report row (rows sharing a segment carry the same merged paragraph)
out = []
for key, n in row_order:
    book, chunk, seg = key
    out.append((book, chunk, seg, newmap[key]))

assert all('\t' not in t and '\n' not in t and '\r' not in t for *_, t in out)
with open(r'AI語譯/_work/review/fix_re4_g2.tsv', 'w', encoding='utf-8', newline='\n') as f:
    for r in out:
        f.write('\t'.join(r) + '\n')

json.dump([list(r) for r in out], open(r'AI語譯/_work/review/_re4g2_out_rows.json', 'w', encoding='utf-8'), ensure_ascii=False)
print('out rows', len(out), 'unique segs', len(newmap), 'skipped', len(skipped))
print('problems', problems)

# show merged paragraphs for segments with several report rows
from collections import Counter
c = Counter(k for k, n in row_order)
f = open(r'AI語譯/_work/review/_re4g2_merged.txt', 'w', encoding='utf-8')
for key, cnt in c.items():
    if cnt > 1:
        f.write("=== %s %s seg=%s rows=%d\n%s\n\n" % (key[0], key[1], key[2], cnt, newmap[key]))
f.close()
