# -*- coding: utf-8 -*-
"""印出某 chunk 指定段（1-based）的現行文字。python _zx1342_show.py 資持記 15d_下三 4 8"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import _zx1342_lib as L

book, chunk = sys.argv[1], sys.argv[2]
o = L.Out(book, chunk)
lines = []
for a in sys.argv[3:]:
    i = int(a)
    lines.append('=== #%d' % i)
    lines.append(o.segs[i - 1])
    lines.append('')
open(os.path.join(os.path.dirname(__file__), '_zx1342_show.txt'), 'w',
     encoding='utf-8').write('\n'.join(lines))
print('n=%d eol=%s' % (len(o.segs), repr(o.eol)))
