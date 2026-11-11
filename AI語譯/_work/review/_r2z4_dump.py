# -*- coding: utf-8 -*-
"""印出某一 resp 檔對應各段的【原文】與現行譯文，供逐條判定。
用法：python _r2z4_dump.py 926 [--full]
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _r2z4_lib import parse_review, load_out

def main():
    n = int(sys.argv[1])
    segs = parse_review(n)
    cache = {}
    for r in segs:
        c = r['chunk']
        if c not in cache:
            cache[c] = load_out(c)['segs']
        cur = cache[c][r['seg'] - 1]
        print('=== %s#%d  (%s)' % (c, r['seg'], r['label'].split('】')[0][1:]))
        print('原：' + r['orig'])
        print('譯：' + cur)
        if cur != r['trans']:
            print('※材料譯文與現行不同：' + r['trans'])
        print()

if __name__ == '__main__':
    main()
