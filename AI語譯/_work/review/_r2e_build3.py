# -*- coding: utf-8 -*-
"""產生 edits_<n>.json；ref 可為 seq 或 seg（先 seq 後 seg 解析）。
用法: import _r2e_build3 as B3; B3.make(n, [(ref, old, new, why), ...], [dict(ref=..,kind=..,reason=..)])
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
import _r2a_lib as L

HERE = os.path.dirname(os.path.abspath(__file__))


def make(n, items, verdicts=None, quiet=False):
    recs = L.parse_review(n)
    byseq = {r['seq']: r for r in recs}
    byseg = {}
    for r in recs:
        byseg.setdefault(r['seg'], []).append(r)
    E, bad, logv = [], [], []
    cache = {}
    for ref, old, new, why in items:
        r = byseq.get(ref)
        if r is None and len(byseg.get(ref, [])) == 1:
            r = byseg[ref][0]
        if r is None:
            bad.append('BAD REF %r' % (ref,))
            continue
        book, chunk, seg = r['book'], r['chunk'], r['seg']
        key = (book, chunk)
        if key not in cache:
            cache[key] = L.Out(book, chunk)
        t = cache[key].segs[seg - 1]
        c = t.count(old)
        if c != 1:
            bad.append('COUNT=%d ref%d %s#%d old=%r' % (c, ref, chunk, seg, old[:60]))
        E.append(dict(book=book, chunk=chunk, seg=seg, old=old, new=new, why=why))
    for v in verdicts or []:
        ref = v['ref']
        r = byseq.get(ref)
        seq = r['seq'] if r else ref
        logv.append(dict(seq=seq, kind=v['kind'], reason=v.get('reason', '')))
    path = os.path.join(HERE, 'edits_%d.json' % n)
    json.dump(dict(n=n, edits=E, verdicts=logv),
              open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    if bad:
        print('!! %d PROBLEMS:' % n)
        for b in bad:
            print('   ' + b)
    if not quiet:
        print('%d: %d edits, %d verdicts' % (n, len(E), len(logv)))
    return path
