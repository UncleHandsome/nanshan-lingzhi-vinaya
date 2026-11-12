# -*- coding: utf-8 -*-
"""在 out 中定位片段並印上下文：python _r2e_ctx.py 09b_卷二之三 "ph1" "ph2" ...
每條印 segment 號與前後約 90 字。找不到時印 NOTFOUND。"""
import os, sys, io
sys.path.insert(0, os.path.dirname(__file__))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import _r2a_lib as L

CH = sys.argv[1]
phrases = sys.argv[2:]
book = '03_業疏'
chunk = CH
if '/' in CH:
    book, chunk = CH.split('/', 1)
o = L.Out(book, chunk)
for ph in phrases:
    hits = []
    for i, s in enumerate(o.segs):
        c = s.count(ph)
        if c:
            hits.append((i + 1, c, s))
    if not hits:
        print('NOTFOUND: %s' % ph)
        continue
    for seg, c, s in hits:
        j = s.find(ph)
        a = max(0, j - 90)
        b = min(len(s), j + len(ph) + 90)
        print('=== #%d (count=%d) %s' % (seg, c, ph))
        print(('…' if a else '') + s[a:j] + '【' + s[j:j + len(ph)] + '】' + s[j + len(ph):b] + ('…' if b < len(s) else ''))
