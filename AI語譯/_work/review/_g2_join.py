#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Rebuild base text: located_all.tsv's `current` is actually `orig`;
recover true vernacular `current` from report_all.tsv by (book,chunk,seg)."""
import io, os, re, json

HERE = os.path.dirname(__file__)


def load(path, sig=False):
    rows = []
    with io.open(path, 'r', encoding='utf-8-sig' if sig else 'utf-8') as f:
        h = f.readline().rstrip('\n').split('\t')
        for ln, line in enumerate(f, start=2):
            fld = line.rstrip('\n').split('\t')
            if len(fld) != len(h):
                continue
            d = dict(zip(h, fld)); d['_line'] = ln
            rows.append(d)
    return rows


rep = load(os.path.join(HERE, 'report_all.tsv'), sig=True)
loc = load(os.path.join(HERE, 'located_all.tsv'))

idx = {}
for r in rep:
    idx.setdefault((r['book'], r['chunk'], r['seg']), []).append(r)

BOOKS = set(['資持記', '01_行事鈔', '04_比丘尼鈔', '05_拾毗尼義鈔'])
sel = [r for r in loc if int(r['votes']) >= 3 and r['book'] in BOOKS]

quotes = re.compile(r'[「『]([^「」『』]{2,40})[」』]')

out, problems = [], []
for r in sel:
    key = (r['book'], r['chunk'], r['seg'])
    cands = idx.get(key, [])
    # disambiguate by orig equality
    pick = None
    for c in cands:
        if c.get('orig', '') == r['orig']:
            pick = c; break
    if pick is None and len(cands) == 1:
        pick = cands[0]
    if pick is None:
        problems.append(('NOMATCH', r['_line'], key, len(cands)))
        continue
    cur = pick['current']
    if not cur.strip():
        problems.append(('EMPTYCUR', r['_line'], key, 0))
        continue
    d = dict(r)
    d['cur2'] = cur
    d['tr2'] = pick.get('tr', '')
    out.append(d)

print('sel', len(sel), 'recovered', len(out), 'problems', len(problems))
for p in problems:
    print('  ', p)

hit = miss = 0
bad = []
for d in out:
    qs = [q for q in quotes.findall(d['problem']) + quotes.findall(d['suggestion']) if len(q) >= 3]
    h = [q for q in qs if q in d['cur2']]
    if qs and not h:
        bad.append(d)
    if h: hit += 1
    else: miss += 1
print('quote hit', hit, 'no-hit', miss)

with io.open(os.path.join(HERE, '_g2_base.json'), 'w', encoding='utf-8') as w:
    json.dump(out, w, ensure_ascii=False, indent=1)

ORDER = ['資持記', '01_行事鈔', '04_比丘尼鈔', '05_拾毗尼義鈔']
out.sort(key=lambda r: (ORDER.index(r['book']), r['chunk'], int(r['seg']) if r['seg'].isdigit() else 0))
with io.open(os.path.join(HERE, '_g2_dump2.txt'), 'w', encoding='utf-8') as w:
    for i, r in enumerate(out, 1):
        w.write('=' * 100 + '\n')
        w.write('[%d] line=%s votes=%s %s %s seg=%s %s %s\n' % (i, r['_line'], r['votes'], r['book'], r['chunk'], r['seg'], r['level'], r['cls']))
        w.write('PROB: %s\n' % r['problem'])
        w.write('SUG : %s\n' % r['suggestion'])
        w.write('ORIG: %s\n' % r['orig'])
        w.write('CUR : %s\n' % r['cur2'])
print('wrote dump2')
