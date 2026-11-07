import io, os, json, importlib.util, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)
ZI = ex.build_zi(ex.sections(), ex.zsecs())

def cmap_of(p):
    fp = os.path.join(B, 'AI語譯', '_work', 'pian_bounds', 'bounds_篇%02d.json' % p)
    if not os.path.exists(fp):
        return {}
    bs = [(int(x['c']), int(x['n'])) for x in json.load(io.open(fp, encoding='utf-8-sig'))['bounds']]
    cm = {}
    for i, (c, n) in enumerate(bs):
        end = bs[i + 1][1] - 1 if i + 1 < len(bs) else 10 ** 6
        for k in range(n, max(n, end) + 1):
            cm[k] = c
    return cm

TARGETS = {16: [68, 108, 118], 17: [9, 13, 17, 48], 18: [25, 47, 103]}
sents = lambda s: [x for x in re.split(r'(?<=[。！？；])', s) if x.strip()]

for p, ns in TARGETS.items():
    cm = cmap_of(p)
    fp = os.path.join(B, 'AI語譯', '_work', 'pian_manual', '篇%02d.json' % p)
    m = {'splits': []}
    if os.path.exists(fp):
        m = json.load(io.open(fp, encoding='utf-8-sig'))
    for n in ns:
        if n in [int(e['n']) for e in m['splits']]:
            continue
        t = ZI[p - 1][n - 1][0]
        ss = sents(t)
        if len(ss) < 2:
            print('跳過(太短)', p, n)
            continue
        c = cm.get(n, 1)
        marker = ss[1][:10]
        if marker not in t:
            print('marker miss', p, n)
            continue
        m['splits'].append({'n': n, 'base': max(1, c - 1), 'markers': [marker], 'targets': [max(1, c - 1), c]})
        print('篇%d 記%d 切點「%s」→ %d/%d' % (p, n, marker, max(1, c - 1), c))
    json.dump(m, io.open(fp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
