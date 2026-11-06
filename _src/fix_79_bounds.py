import io, os, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'

def setb(p, pairs):
    fp = os.path.join(B, 'AI語譯', '_work', 'pian_bounds', 'bounds_篇%02d.json' % p)
    d = json.load(io.open(fp, encoding='utf-8-sig'))
    mp = {x['c']: x for x in d['bounds']}
    for c, n in pairs.items():
        if c in mp:
            mp[c]['n'] = n
    json.dump(d, io.open(fp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('篇%d' % p, [(x['c'], x['n']) for x in d['bounds'] if x['c'] in pairs])

setb(7, {2: 8, 3: 9, 18: 32, 47: 108, 48: 110})
setb(9, {7: 16, 8: 19, 9: 20, 10: 25})
