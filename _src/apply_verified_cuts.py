import io, os, json, importlib.util

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)
ZI = ex.build_zi(ex.sections(), ex.zsecs())

PROP = [
    (16, 68, '第九，示法中，初科'),
    (16, 108, '捨罪，對僧乞中'),
    (17, 9, '釋名中。'),
    (17, 13, '三中，《大悲經》'),
    (17, 17, '第二作之方法，求財中'),
    (17, 48, '六中。'),
    (18, 25, '盡形，藥體中，《僧祇'),
    (18, 47, '正加，通簡中'),
    (18, 103, '三中。'),
]

def cmap_of(p):
    fp = os.path.join(B, 'AI語譯', '_work', 'pian_bounds', 'bounds_篇%02d.json' % p)
    bs = [(int(x['c']), int(x['n'])) for x in json.load(io.open(fp, encoding='utf-8-sig'))['bounds']]
    cm = {}
    for i, (c, n) in enumerate(bs):
        end = bs[i + 1][1] - 1 if i + 1 < len(bs) else 10 ** 6
        for k in range(n, max(n, end) + 1):
            cm[k] = c
    return cm

for p in (16, 17, 18):
    cm = cmap_of(p)
    fp = os.path.join(B, 'AI語譯', '_work', 'pian_manual', '篇%02d.json' % p)
    m = json.load(io.open(fp, encoding='utf-8-sig')) if os.path.exists(fp) else {'splits': []}
    arr = [x for x in PROP if x[0] == p]
    nums = {n for _, n, _ in arr}
    m['splits'] = [e for e in m.get('splits', []) if int(e['n']) not in nums]
    for _, n, mk in arr:
        t = ZI[p - 1][n - 1][0]
        cnt = t.count(mk)
        if cnt == 0:
            print('MISS', p, n, mk)
            continue
        c = cm.get(n, 1)
        m['splits'].append({'n': n, 'base': max(1, c - 1), 'markers': [mk], 'targets': [max(1, c - 1), c]})
        print('篇%d 記%d 「%s」x%d → %d/%d' % (p, n, mk, cnt, max(1, c - 1), c))
    json.dump(m, io.open(fp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
