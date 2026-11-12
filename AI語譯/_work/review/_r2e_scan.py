# -*- coding: utf-8 -*-
"""r2 1649-1760 掃描：每檔段數、chunk 分佈、材料譯文 vs out 現行 ratio。
用法: python _r2e_scan.py [起] [迄] [--bad]
"""
import os, sys, io, difflib, collections
sys.path.insert(0, os.path.dirname(__file__))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import _r2a_lib as L

A = int(sys.argv[1]) if len(sys.argv) > 1 and not sys.argv[1].startswith('-') else 1649
B = int(sys.argv[2]) if len(sys.argv) > 2 and not sys.argv[2].startswith('-') else 1760
SHOW_BAD = '--bad' in sys.argv


def norm(s):
    return ''.join(ch for ch in (s or '') if ch not in ' \t\r\n')


def main():
    books = collections.Counter()
    bad = []
    rows = []
    miss = []
    for n in range(A, B + 1):
        p = os.path.join(L.REV, '校閱_%d.txt' % n)
        if not os.path.exists(p):
            miss.append(n)
            continue
        recs = L.parse_review(n)
        if not recs:
            print('##### %d NO MATERIAL' % n)
            continue
        cache = {}
        mins = 1.0
        seek = collections.Counter()
        for r in recs:
            k = (r['book'], r['chunk'])
            books[k] += 1
            if k not in cache:
                cache[k] = L.Out(*k)
            o = cache[k]
            seek[k] += 1
            if r['seg'] - 1 >= len(o.segs) or r['seg'] < 1:
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
        rows.append((n, len(recs), mins, seek))
        if SHOW_BAD:
            print('%d segs=%d min=%.3f %s' % (n, len(recs), mins,
                  ' '.join('%s/%s:%d(n=%d)' % (k[0], k[1], v, len(cache[k].segs)) for k, v in seek.items())))
    print('FILES=%d SEGS=%d' % (len(rows), sum(r[1] for r in rows)))
    print('MISSING: %s' % (miss,))
    print('BOOKS:')
    for k, v in sorted(books.items()):
        o = L.Out(*k)
        print('  %s/%s  %d  (chunk segs=%d, eol=%s)' % (k[0], k[1], v, len(o.segs),
              'CRLF' if o.eol == '\r\n' else 'LF'))
    print('MISMATCH=%d' % len(bad))
    for b in bad:
        print('  BAD', b)
    low = [r for r in rows if r[2] < 0.999]
    print('FILES_BELOW_0.999=%d' % len(low))
    for n, cnt, mins, _ in low:
        print('  LOW %d segs=%d min=%.3f' % (n, cnt, mins))


if __name__ == '__main__':
    main()
