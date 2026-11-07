# -*- coding: utf-8 -*-
import io, os, re, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
SRC = os.path.join(B, '會本材料_11-30')
BD = os.path.join(B, 'AI語譯', '_work', 'pian_bounds')
SD = os.path.join(B, 'AI語譯', '_work', 'pian_split_out')

for fn, kind in (('b2.json', 'bounds'), ('s2.json', 'splits')):
    fp = os.path.join(SRC, fn)
    if not os.path.exists(fp):
        print('missing', fn)
        continue
    d = json.load(io.open(fp, encoding='utf-8-sig'))
    for key, val in d.items():
        m = re.search(r'篇(\d+)', key)
        if not m:
            print('skip key', key)
            continue
        p = int(m.group(1))
        if kind == 'bounds':
            bs = val.get('bounds', val if isinstance(val, list) else [])
            json.dump({'bounds': bs}, io.open(os.path.join(BD, 'bounds_篇%02d.json' % p), 'w', encoding='utf-8'),
                      ensure_ascii=False, indent=1)
            print('篇%d bounds %d' % (p, len(bs)))
        else:
            sp = val.get('splits', val if isinstance(val, list) else [])
            json.dump({'splits': sp}, io.open(os.path.join(SD, 'split_篇%02d.json' % p), 'w', encoding='utf-8'),
                      ensure_ascii=False, indent=1)
            print('篇%d splits %d' % (p, len(sp)))
