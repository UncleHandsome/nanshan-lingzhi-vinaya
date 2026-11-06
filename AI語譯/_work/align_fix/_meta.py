# -*- coding: utf-8 -*-
import json, os, io

D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\align_fix'
rows = []
for f in sorted(os.listdir(D)):
    if not f.endswith('.json') or f.startswith('out_'):
        continue
    d = json.load(io.open(os.path.join(D, f), encoding='utf-8'))
    items, cand = d.get('items', []), d.get('cand', [])
    zs = [i['z'] for i in items]
    cs = [c['c'] for c in cand]
    rows.append((f, d.get('sec'), d.get('name'), len(items), len(cand),
                 zs[0] if zs else None, zs[-1] if zs else None,
                 cs[0] if cs else None, cs[-1] if cs else None,
                 [k for k in d.keys()]))
out = io.StringIO()
for r in rows:
    out.write('%-10s sec=%-3s name=%-12s items=%-3d cand=%-3d z=%s..%s c=%s..%s %s\n' % r)
out.write('\nkeys of 005: %s\n' % rows[4][9])
io.open(os.path.join(D, '_meta.txt'), 'w', encoding='utf-8').write(out.getvalue())
print('ok')
