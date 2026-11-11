# -*- coding: utf-8 -*-
"""段號對位檢查：材料【譯文】vs out 同段，相似度低者找最佳段。
用法: python _r2a_align.py 1000 1330
"""
import os, sys, difflib
sys.path.insert(0, os.path.dirname(__file__))
import _r2a_lib as L

n0, n1 = int(sys.argv[1]), int(sys.argv[2])
cache = {}
bad = []
tot = 0
for n in range(n0, n1 + 1):
    for r in L.parse_review(n):
        key = (r['book'], r['chunk'])
        if key not in cache:
            o = L.Out(*key)
            bp = os.path.join(L.BKBASE, r['book'], r['chunk'] + '_g.txt')
            if os.path.exists(bp):
                bs = L.decode(L.rd(bp))
                be = '\r\n' if '\r\n' in bs else '\n'
                ps = bs.split(be + be)
                if ps and ps[-1] == '':
                    ps = ps[:-1]
                o.segs = ps
            cache[key] = o
        o = cache[key]
        mat = (r['trans'] or '').replace('\n', '')
        tot += 1
        if not mat:
            bad.append((n, r['seq'], r['chunk'], r['seg'], 'NOMAT', 0, -1))
            continue
        if r['seg'] - 1 < len(o.segs):
            cur = o.segs[r['seg'] - 1]
            ratio = difflib.SequenceMatcher(None, mat, cur).ratio()
        else:
            ratio = 0.0
        if ratio >= 0.94:
            continue
        # 找最佳
        best, bi = 0.0, -1
        for i, s in enumerate(o.segs):
            rr = difflib.SequenceMatcher(None, mat, s).ratio()
            if rr > best:
                best, bi = rr, i + 1
        bad.append((n, r['seq'], r['chunk'], r['seg'], 'LOW', round(ratio, 3), bi, round(best, 3)))
print('total segs', tot, 'suspect', len(bad))
for b in bad[:60]:
    print(b)
