# -*- coding: utf-8 -*-
"""印出某校閱檔的全部段（原文＋現行譯文），供逐條判定。用法: python _r2a_view.py 1000 [--mat]"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import _r2a_lib as L

n = int(sys.argv[1])
show_mat_diff = '--mat' in sys.argv
cache = {}
for r in L.parse_review(n):
    key = (r['book'], r['chunk'])
    if key not in cache:
        cache[key] = L.Out(*key)
    o = cache[key]
    cur = o.segs[r['seg'] - 1] if r['seg'] - 1 < len(o.segs) else '<MISSING>'
    mat = r['trans'] or ''
    mark = '' if cur.replace('\n', '') == mat.replace('\n', '') else '  [MAT!=CUR]'
    print('=== %d-%04d %s/%s#%d%s' % (r['batch'], r['seq'], r['book'], r['chunk'], r['seg'], mark))
    print('原: ' + (r['orig'] or ''))
    print('譯: ' + cur)
    if show_mat_diff and mark:
        print('材: ' + mat)
    print()
