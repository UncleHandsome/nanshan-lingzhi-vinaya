# -*- coding: utf-8 -*-
"""印某檔材料 seq→chunk/seg 對照，以及該檔各段 out 現行文字（可指定段號）。
用法: python _r2x_segs.py 1775 [16 23 ...]
"""
import os, sys, io
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import _r2a_lib as L


def main():
    n = int(sys.argv[1])
    want = set(int(x) for x in sys.argv[2:]) if len(sys.argv) > 2 else None
    recs = L.parse_review(n)
    cache = {}
    print('== %d: %d segs: %s' % (n, len(recs),
          ' '.join('%d:%s/%s#%d' % (r['seq'], r['book'][:2], r['chunk'][:3], r['seg']) for r in recs)))
    last = None
    for r in recs:
        k = (r['book'], r['chunk'])
        if k not in cache:
            cache[k] = L.Out(*k)
        if want is not None and r['seg'] not in want:
            continue
        if k != last:
            print('---- %s/%s' % k)
            last = k
        print('#%d|%s' % (r['seg'], cache[k].segs[r['seg'] - 1]))


if __name__ == '__main__':
    main()
