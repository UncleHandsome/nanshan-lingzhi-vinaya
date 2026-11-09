# -*- coding: utf-8 -*-
import io, csv, re, collections
p = r'AI語譯/_work/review/fix_re4_g2.tsv'
lines = io.open(p, encoding='utf-8').read().split('\n')
print('trailing empty:', lines[-1] == '')
lines = [l for l in lines if l]
print('lines', len(lines))
bad = 0
seen = collections.Counter()
rows = []
for i, l in enumerate(lines):
    f = l.split('\t')
    if len(f) != 4:
        print('BADCOLS', i, len(f)); bad += 1; continue
    rows.append(f)
keys = [(r[0], r[1], r[2]) for r in rows]
print('unique keys', len(set(keys)), 'of', len(keys))
print('books', collections.Counter(r[0] for r in rows))
# bracket balance & ascii
pairs = [('（', '）'), ('「', '」'), ('〔', '〕'), ('《', '》'), ('〈', '〉'), ('『', '』'), ('［', '］')]
for i, r in enumerate(rows):
    t = r[3]
    for a, b in pairs:
        if t.count(a) != t.count(b):
            print('UNBAL', i, r[0], r[1], r[2], a, t.count(a), t.count(b)); bad += 1
    if re.search(r'[A-Za-z]', t):
        print('LATIN', i, r[2], re.findall(r'[A-Za-z]+', t)); bad += 1
    if '  ' in t:
        print('DBLSPACE', i, r[2]); bad += 1
print('bad', bad)
# also check the current(original) had balanced brackets, to compare deltas
rows0 = __import__('json').load(open(r'AI語譯/_work/review/_re4g2_rows.json', encoding='utf-8'))
cur = {(d['book'], d['chunk'], d['seg']): d['current'] for d in rows0}
for i, r in enumerate(rows):
    t = r[3]; c = cur[(r[0], r[1], r[2])]
    for a, b in pairs:
        if (c.count(a) - c.count(b)) != (t.count(a) - t.count(b)):
            print('DELTA', i, r[1], r[2], a, c.count(a), c.count(b), t.count(a), t.count(b))
