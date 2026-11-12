# -*- coding: utf-8 -*-
"""檢查 edits 檔每條 old 在該段出現次數。用法: python _r2c_check.py _r2c_edits_X.txt"""
import os, sys, io
sys.path.insert(0, os.path.dirname(__file__))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import _r2a_lib as L


def parse(path):
    blocks = {}
    n = None
    book = chunk = None
    for ln in open(path, encoding='utf-8-sig'):
        ln = ln.rstrip('\n').rstrip('\r')
        if not ln.strip():
            continue
        if ln.startswith('### '):
            n = int(ln[4:].strip()); blocks[n] = []; book = chunk = None; continue
        if ln.startswith('@@ '):
            v = ln[3:].strip()
            if v == '-':
                book, chunk = '-', '-'
            else:
                book, chunk = v.split('/')
            continue
        seg, old, new = ln.split('\t')
        blocks[n].append(dict(book=book, chunk=chunk, seg=int(seg), old=old, new=new))
    return blocks


path = sys.argv[1]
blocks = parse(path)
for n in sorted(blocks):
    recs = {r['seq']: r for r in L.parse_review(n)}
    for e in blocks[n]:
        if e['book'] == '-':
            r = recs[e['seg']]
            e['book'], e['chunk'], e['seg'] = r['book'], r['chunk'], r['seg']
    cache = {}
    for i, e in enumerate(blocks[n]):
        k = (e['book'], e['chunk'])
        if k not in cache:
            cache[k] = L.Out(*k)
        t = cache[k].segs[e['seg'] - 1]
        c = t.count(e['old'])
        mark = 'OK ' if c == 1 else ('MISS' if c == 0 else 'DUP%d' % c)
        print('%s %d#%d [%d] %s' % (mark, n, e['seg'], i, e['old'][:60]))
