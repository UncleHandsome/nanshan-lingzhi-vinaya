# -*- coding: utf-8 -*-
"""對位檢查：材料每段【譯文】與 out 各段做相似度比對，回報最佳段序與比值。
用法: python _r2b_align.py 1331 1332 ...
"""
import os, sys, difflib
sys.path.insert(0, os.path.dirname(__file__))
import _r2a_lib as L


def norm(s):
    return ''.join(ch for ch in (s or '') if ch not in ' \t\r\n')


def check(n, thr=0.94, verbose=True):
    recs = L.parse_review(n)
    cache = {}
    bad = []
    for r in recs:
        key = (r['book'], r['chunk'])
        if key not in cache:
            cache[key] = L.Out(*key)
        o = cache[key]
        mat = norm(r['trans'])
        cur = norm(o.segs[r['seg'] - 1]) if r['seg'] - 1 < len(o.segs) else ''
        same = difflib.SequenceMatcher(None, mat, cur).ratio()
        best = (0, -1)
        if same < thr:
            for i, s in enumerate(o.segs):
                rt = difflib.SequenceMatcher(None, mat, norm(s)).ratio()
                if rt > best[0]:
                    best = (rt, i + 1)
        flag = '' if same >= thr else ' MISMATCH best#%d %.3f' % (best[1], best[0])
        if same < thr:
            bad.append((r['seq'], r['seg'], same, best))
        if verbose:
            print('%d-%04d %s/%s#%d n=%d ratio=%.3f%s' % (r['batch'], r['seq'], r['book'],
                                                          r['chunk'], r['seg'], len(o.segs), same, flag))
    return bad


if __name__ == '__main__':
    for a in sys.argv[1:]:
        if not a.isdigit():
            continue
        print('##### %s' % a)
        bad = check(int(a))
        print('##### %s bad=%d %s' % (a, len(bad), bad[:6]))
