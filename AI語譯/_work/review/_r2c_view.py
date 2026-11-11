# -*- coding: utf-8 -*-
"""輸出某檔的原文＋現行譯文（含相似度定位結果），供逐檔判讀。
用法: python _r2c_view.py 1342 [1343 ...]
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import _r2c_lib as L

outdir = os.path.join(os.path.dirname(__file__), '_r2c_v')
os.makedirs(outdir, exist_ok=True)

for a in sys.argv[1:]:
    if not a.isdigit():
        continue
    n = int(a)
    recs = L.parse_review(n)
    lines = []
    for r in recs:
        seg, ratio, moved = L.locate(r['book'], r['chunk'], r['trans'], r['seg'])
        o = L.out_for(r['book'], r['chunk'])
        cur = o.segs[seg - 1] if 1 <= seg <= len(o.segs) else '<OUT OF RANGE>'
        flag = '' if (not moved and ratio >= 0.94) else '  <<< RELOC seg=%d ratio=%.3f' % (seg, ratio)
        lines.append('=== %d-%04d  %s/%s#%d%s' % (n, r['seq'], r['book'], r['chunk'], seg, flag))
        lines.append('【原文】' + (r['orig'] or ''))
        lines.append('【譯文】' + cur)
        lines.append('')
    p = os.path.join(outdir, '%d.txt' % n)
    open(p, 'w', encoding='utf-8').write('\n'.join(lines))
    print('wrote', p, len(recs))
