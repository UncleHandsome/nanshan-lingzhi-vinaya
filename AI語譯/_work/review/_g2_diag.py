#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Diagnose whether `current` in located_all.tsv is really a vernacular translation."""
import io, os, re, sys, json

HERE = os.path.dirname(__file__)
SRC = os.path.join(HERE, 'located_all.tsv')

rows = []
with io.open(SRC, 'r', encoding='utf-8') as f:
    header = f.readline().rstrip('\n').split('\t')
    for ln, line in enumerate(f, start=2):
        fld = line.rstrip('\n').split('\t')
        if len(fld) != len(header):
            continue
        d = dict(zip(header, fld)); d['_line'] = ln
        rows.append(d)

BOOKS = set(['資持記', '01_行事鈔', '04_比丘尼鈔', '05_拾毗尼義鈔'])
sel = [r for r in rows if int(r['votes']) >= 3 and r['book'] in BOOKS]

# classical-marker heuristic: does current look like wenyan? count of 之/其/故/是以/云 etc vs 的/了/這
def wenyan_score(s):
    wy = sum(s.count(c) for c in '之其故云謂即此乃為以於而')
    col = sum(s.count(c) for c in '的了這著們個時說會')
    return wy, col

quotes = re.compile(r'[「『]([^「」『』]{2,40})[」』]')

stats = {'cur_eq_orig': 0, 'cur_ne_orig': 0, 'quote_hit': 0, 'quote_miss': 0, 'no_quote': 0}
detail = []
for r in sel:
    eq = (r['orig'] == r['current'])
    stats['cur_eq_orig' if eq else 'cur_ne_orig'] += 1
    qs = quotes.findall(r['problem']) + quotes.findall(r['suggestion'])
    qs = [q for q in qs if len(q) >= 3]
    hit = [q for q in qs if q in r['current']]
    miss = [q for q in qs if q not in r['current']]
    if not qs:
        stats['no_quote'] += 1
    if hit:
        stats['quote_hit'] += 1
    if miss:
        stats['quote_miss'] += 1
    wy, col = wenyan_score(r['current'])
    detail.append(dict(line=r['_line'], book=r['book'], chunk=r['chunk'], seg=r['seg'],
                       eq=eq, nq=len(qs), hit=len(hit), miss=len(miss),
                       wy=wy, col=col, curlen=len(r['current'])))

print('rows', len(sel))
print(stats)
print()
print('%-6s %-10s %-6s %-5s %-4s %-4s %-4s %-5s %-4s %s' % ('line','book','chunk','seg','eq','nq','hit','miss','wy/col','curlen'))
for d in detail:
    print('%-6d %-10s %-6s %-5s %-4s %-4d %-4d %-5d %-4s %d' % (
        d['line'], d['book'], d['chunk'], d['seg'], 'Y' if d['eq'] else 'n',
        d['nq'], d['hit'], d['miss'], '%d/%d' % (d['wy'], d['col']), d['curlen']))
