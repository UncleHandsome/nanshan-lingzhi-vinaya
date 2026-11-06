import json, os, io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
for p in [2, 3, 4, 5]:
    fp = os.path.join(B, 'AI語譯', '_work', 'pian_bounds', 'bounds_篇%02d.json' % p)
    d = json.load(io.open(fp, encoding='utf-8-sig'))
    bs = [(int(x['c']), int(x['n'])) for x in d['bounds']]
    print('篇%d bounds:' % p, bs[:6], '...', bs[-3:])
