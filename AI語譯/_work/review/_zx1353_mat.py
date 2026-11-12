# -*- coding: utf-8 -*-
"""輸出材料段（原文＋現行譯文），去掉提示詞。用法: python _zx1353_mat.py 1353 1354"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import _zx1353_lib as L

d = os.path.join(os.path.dirname(__file__), '_zx1353_m')
os.makedirs(d, exist_ok=True)
for a in sys.argv[1:]:
    if not a.isdigit():
        continue
    n = int(a)
    recs = L.parse_review(n)
    out = []
    for r in recs:
        out.append('### %d-%04d %s/%s#%d' % (n, r['seq'], r['book'], r['chunk'], r['seg']))
        out.append('原：' + (r['orig'] or ''))
        out.append('譯：' + (r['trans'] or ''))
        out.append('')
    open(os.path.join(d, '%d.txt' % n), 'w', encoding='utf-8').write('\n'.join(out))
    print('mat', n, len(recs))
