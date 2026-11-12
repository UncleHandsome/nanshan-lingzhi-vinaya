# -*- coding: utf-8 -*-
"""產生 edits_<n>.json；依材料 seq 自動取 book/chunk/seg，並驗 old 恰出現一次。
用法（per-batch 腳本）:
    import _r2d_build as B
    B.make(1533, [(1, old, new, why), ...], [dict(seq=1,kind='真錯',reason='..'), ...])
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
import _r2a_lib as L

HERE = os.path.dirname(os.path.abspath(__file__))


def make(n, items, verdicts=None, quiet=False):
    m = {r['seq']: (r['book'], r['chunk'], r['seg']) for r in L.parse_review(n)}
    E, bad = [], []
    cache = {}
    for seq, old, new, why in items:
        if seq not in m:
            bad.append('BAD SEQ %r' % (seq,))
            continue
        book, chunk, seg = m[seq]
        key = (book, chunk)
        if key not in cache:
            cache[key] = L.Out(book, chunk)
        t = cache[key].segs[seg - 1]
        c = t.count(old)
        if c != 1:
            bad.append('COUNT=%d seq%d %s#%d old=%r' % (c, seq, chunk, seg, old[:50]))
        E.append(dict(book=book, chunk=chunk, seg=seg, old=old, new=new, why=why))
    path = os.path.join(HERE, 'edits_%d.json' % n)
    json.dump(dict(n=n, edits=E, verdicts=verdicts or []),
              open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    if bad:
        print('!! %d PROBLEMS:' % n)
        for b in bad:
            print('   ' + b)
    if not quiet:
        print('%d: %d edits, %d verdicts' % (n, len(E), len(verdicts or [])))
    return path
