# -*- coding: utf-8 -*-
"""印指定段：python _r2e_seg.py 1668 98 103 104
參數可用段號(seg)；若 <1000 且不在 seg 範圍，則當 seq。"""
import os, sys, io
sys.path.insert(0, os.path.dirname(__file__))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import _r2a_lib as L


def main():
    n = int(sys.argv[1])
    recs = L.parse_review(n)
    segs = set(r['seg'] for r in recs)
    wants = [int(x) for x in sys.argv[2:]]
    cache = {}
    for r in recs:
        if r['seg'] not in wants and r['seq'] not in wants:
            continue
        k = (r['book'], r['chunk'])
        if k not in cache:
            cache[k] = L.Out(*k)
        cur = cache[k].segs[r['seg'] - 1]
        print('=== #%d（seq%d）#%d' % (r['seq'], r['seq'], r['seg']))
        print('原: ' + (r['orig'] or ''))
        print('譯: ' + cur)


if __name__ == '__main__':
    main()
