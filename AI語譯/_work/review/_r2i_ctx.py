# -*- coding: utf-8 -*-
"""印出某段中關鍵字前後文：python _r2i_ctx.py 10b_中三下 38 後念 動機 ..."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _r2i_lib as L

chunk = sys.argv[1]
seg = int(sys.argv[2])
keys = [k for k in sys.argv[3:] if not k.startswith('--out=')]
out = None
for k in sys.argv[3:]:
    if k.startswith('--out='):
        out = k.split('=', 1)[1]
o = L.load_out(chunk)
t = o['segs'][seg - 1]
buf = ['== %s#%d (%d chars)' % (chunk, seg, len(t))]
if not keys:
    buf.append(t)
for k in keys:
    i = t.find(k)
    if i < 0:
        buf.append('  [%s] NOT FOUND' % k)
        continue
    a = max(0, i - 70)
    b = min(len(t), i + len(k) + 70)
    buf.append('  [%s] ...%s...' % (k, t[a:b]))
txt = '\n'.join(buf)
if out:
    open(out, 'w', encoding='utf-8').write(txt)
    print('wrote', out)
else:
    print(txt)
