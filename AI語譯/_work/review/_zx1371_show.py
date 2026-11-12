# -*- coding: utf-8 -*-
"""顯示某檔：回應全文 + 各段原文/現行譯文（out 實文）。
用法: python _zx1371_show.py 1371 [1372 ...]
輸出 _zx1371_v/<n>.txt
"""
import os, sys, difflib
sys.path.insert(0, os.path.dirname(__file__))
import _zx1353_lib as L

D = os.path.join(os.path.dirname(__file__), '_zx1371_v')
os.makedirs(D, exist_ok=True)


def one(n):
    recs = L.parse_review(n)
    rp = os.path.join(L.RESP, 'resp_%d.txt' % n)
    resp = open(rp, encoding='utf-8').read().strip() if os.path.exists(rp) else '（無回應檔）'
    out = ['===== resp_%d.txt（%d 字）=====' % (n, len(resp)), resp, '', '===== 材料 %d 段 =====' % len(recs)]
    cache = {}
    for r in recs:
        k = (r['book'], r['chunk'])
        if k not in cache:
            cache[k] = L.out_for(*k)
        o = cache[k]
        seg, ratio, moved = L.locate(r['book'], r['chunk'], r['trans'], r['seg'])
        t = o.segs[seg - 1] if 1 <= seg <= len(o.segs) else '（越界）'
        out.append('--- %d-%04d %s/%s#%d  ratio=%.3f%s' % (
            n, r['seq'], r['book'], r['chunk'], r['seg'], ratio, ' MOVED->%d' % seg if moved else ''))
        out.append('原：' + (r['orig'] or ''))
        out.append('譯：' + t)
        out.append('')
    p = os.path.join(D, '%d.txt' % n)
    open(p, 'w', encoding='utf-8').write('\n'.join(out))
    print(p, len('\n'.join(out)))


for a in sys.argv[1:]:
    if a.isdigit():
        one(int(a))
