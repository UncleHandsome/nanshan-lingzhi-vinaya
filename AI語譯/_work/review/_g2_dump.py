#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Dump the selected rows of located_all.tsv into a readable review file."""
import io, os, sys, json

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SRC = os.path.join(os.path.dirname(__file__), 'located_all.tsv')

rows = []
with io.open(SRC, 'r', encoding='utf-8') as f:
    header = f.readline().rstrip('\n').split('\t')
    for ln, line in enumerate(f, start=2):
        line = line.rstrip('\n')
        if not line:
            continue
        fld = line.split('\t')
        if len(fld) != len(header):
            print('BAD COL COUNT line', ln, len(fld), file=sys.stderr)
            continue
        d = dict(zip(header, fld))
        d['_line'] = ln
        rows.append(d)

BOOKS = set(['資持記', '01_行事鈔', '04_比丘尼鈔', '05_拾毗尼義鈔'])
sel = [r for r in rows if int(r['votes']) >= 3 and r['book'] in BOOKS]

# ordering: by book order given, then chunk, seg
ORDER = ['資持記', '01_行事鈔', '04_比丘尼鈔', '05_拾毗尼義鈔']
sel.sort(key=lambda r: (ORDER.index(r['book']), r['chunk'], int(r['seg']) if r['seg'].isdigit() else 0))

print('selected', len(sel))
print('chars: orig=%d current=%d problem=%d suggestion=%d' % (
    sum(len(r['orig']) for r in sel), sum(len(r['current']) for r in sel),
    sum(len(r['problem']) for r in sel), sum(len(r['suggestion']) for r in sel)))

out = os.path.join(os.path.dirname(__file__), '_g2_dump.txt')
with io.open(out, 'w', encoding='utf-8') as w:
    for i, r in enumerate(sel, 1):
        w.write('=' * 100 + '\n')
        w.write('[%d] line=%s votes=%s book=%s chunk=%s seg=%s level=%s\n' % (
            i, r['_line'], r['votes'], r['book'], r['chunk'], r['seg'], r['level']))
        w.write('cls: %s\n' % r['cls'])
        w.write('PROBLEM: %s\n' % r['problem'])
        w.write('SUGGEST: %s\n' % r['suggestion'])
        w.write('ORIG   : %s\n' % r['orig'])
        w.write('CURRENT: %s\n' % r['current'])
print('wrote', out)

# also save json for programmatic access
with io.open(os.path.join(os.path.dirname(__file__), '_g2_sel.json'), 'w', encoding='utf-8') as w:
    json.dump(sel, w, ensure_ascii=False, indent=1)
print('wrote json')
