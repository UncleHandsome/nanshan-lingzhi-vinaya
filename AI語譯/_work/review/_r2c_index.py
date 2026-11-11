# -*- coding: utf-8 -*-
"""r2 1491-1648：索引 + 全量對位檢查（只看異常，輸出精簡）。
用法: python _r2c_index.py [--full]
"""
import os, sys, io, difflib, collections
sys.path.insert(0, os.path.dirname(__file__))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import _r2a_lib as L

A, B = 1491, 1648


def norm(s):
    return ''.join(ch for ch in (s or '') if ch not in ' \t\r\n')


def main():
    full = '--full' in sys.argv
    books = collections.Counter()
    tot_segs = 0
    bad = []
    stale = []
    rows = []
    for n in range(A, B + 1):
        recs = L.parse_review(n)
        if not recs:
            print('##### %d NO MATERIAL' % n)
            continue
        keys = []
        cache = {}
        mins = 1.0
        for r in recs:
            k = (r['book'], r['chunk'])
            books[k] += 1
            if k not in cache:
                cache[k] = L.Out(*k)
            o = cache[k]
            if r['seg'] - 1 >= len(o.segs):
                bad.append((n, r['seq'], r['seg'], 'RANGE', len(o.segs)))
                continue
            cur = o.segs[r['seg'] - 1]
            rt = difflib.SequenceMatcher(None, norm(r['trans']), norm(cur)).ratio()
            mins = min(mins, rt)
            if rt < 0.94:
                best = (0, -1)
                for i, s in enumerate(o.segs):
                    rr = difflib.SequenceMatcher(None, norm(r['trans']), norm(s)).ratio()
                    if rr > best[0]:
                        best = (rr, i + 1)
                bad.append((n, r['seq'], r['seg'], round(rt, 3), 'best#%d %.3f' % best))
            elif rt < 0.999:
                stale.append((n, r['seq'], r['seg'], round(rt, 3)))
            if k not in [x[0] for x in keys]:
                keys.append((k, len(o.segs), o.eol))
        tot_segs += len(recs)
        rows.append((n, len(recs), mins, keys))
        if full:
            print('%d segs=%d min=%.3f %s' % (n, len(recs), mins,
                  ' '.join('%s/%s(n=%d,%s)' % (k[0], k[1], ln, 'CRLF' if e == '\r\n' else 'LF')
                           for k, ln, e in keys)))
    print('FILES=%d SEGS=%d' % (len(rows), tot_segs))
    print('BOOKS:')
    for k, v in sorted(books.items()):
        print('  %s/%s  %d' % (k[0], k[1], v))
    print('MISMATCH=%d' % len(bad))
    for b in bad:
        print('  BAD', b)
    print('NEAR(0.94-0.999)=%d' % len(stale))
    for s in stale[:80]:
        print('  NEAR', s)


if __name__ == '__main__':
    main()
