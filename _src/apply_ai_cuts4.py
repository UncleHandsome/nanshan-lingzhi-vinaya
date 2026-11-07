import io, os, json, importlib.util

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)
ZI = ex.build_zi(ex.sections(), ex.zsecs())

def cmap_of(p):
    fp = os.path.join(B, 'AI語譯', '_work', 'pian_bounds', 'bounds_篇%02d.json' % p)
    bs = [(int(x['c']), int(x['n'])) for x in json.load(io.open(fp, encoding='utf-8-sig'))['bounds']]
    cm = {}
    for i, (c, n) in enumerate(bs):
        end = bs[i + 1][1] - 1 if i + 1 < len(bs) else 10 ** 6
        for k in range(n, max(n, end) + 1):
            cm[k] = c
    return cm

OPS = [
    (1, 444, 'cut', '問中'),
    (1, 449, 'cut', '好作下'),
    (5, 77, 'move', 32),
    (5, 78, 'cut', '初問白讀'),
    (5, 79, 'move', 33),
    (5, 80, 'cut', '問互作中'),
    (5, 86, 'move', 36),
    (29, 10, 'cut', '四中'),
    (29, 21, 'cut', '三中'),
    (30, 23, 'move', 21),
    (30, 1, 'cut', '30 釋諸部篇'),
]

for p in sorted({o[0] for o in OPS}):
    fp = os.path.join(B, 'AI語譯', '_work', 'pian_manual', '篇%02d.json' % p)
    m = json.load(io.open(fp, encoding='utf-8-sig')) if os.path.exists(fp) else {'splits': []}
    ops = [o for o in OPS if o[0] == p]
    nums = {o[1] for o in ops}
    m['splits'] = [e for e in m.get('splits', []) if int(e['n']) not in nums]
    cm = cmap_of(p)
    for _, n, kind, arg in ops:
        t = ZI[p - 1][n - 1][0]
        if kind == 'move':
            m['splits'].append({'n': n, 'base': int(arg)})
            print('篇%d 記%d 整條搬到鈔%d' % (p, n, arg))
        else:
            if arg not in t:
                print('MISS', p, n, arg); continue
            c = max(2, cm.get(n, 2))
            m['splits'].append({'n': n, 'base': c - 1, 'markers': [arg], 'targets': [c - 1, c]})
            print('篇%d 記%d 切在「%s」之前 → 鈔%d/%d' % (p, n, arg, c - 1, c))
    json.dump(m, io.open(fp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
