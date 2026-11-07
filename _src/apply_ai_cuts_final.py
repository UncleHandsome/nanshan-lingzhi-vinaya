import io, os, json, importlib.util

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
CUTS = {
    3: [(24, '隔障中二'), (25, '第二例中'), (26, '釋疑中')],
    4: [(50, '結斷中'), (52, '三中有二')],
    5: [(70, '第三段為二'), (71, '結文中'), (78, '初問白讀'), (79, '呪術例中'), (80, '問互作中')],
    7: [(7, '化教，標中')],
    8: [(122, '父母中'), (124, '奴中')],
    17: [(179, '檀越施，釋名義中')],
    22: [(68, '次造塔中')],
}
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

for p, arr in CUTS.items():
    cm = cmap_of(p)
    fp = os.path.join(B, 'AI語譯', '_work', 'pian_manual', '篇%02d.json' % p)
    m = json.load(io.open(fp, encoding='utf-8-sig')) if os.path.exists(fp) else {'splits': []}
    nums = {n for n, _ in arr}
    m['splits'] = [e for e in m.get('splits', []) if int(e['n']) not in nums]
    for n, mk in arr:
        t = ZI[p - 1][n - 1][0]
        if mk not in t:
            print('MISS', p, n, mk); continue
        c = cm.get(n, 1)
        m['splits'].append({'n': n, 'base': max(1, c - 1), 'markers': [mk], 'targets': [max(1, c - 1), c]})
        print('篇%d 記%d 「%s」→ %d/%d' % (p, n, mk, max(1, c - 1), c))
    json.dump(m, io.open(fp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# 篇1 最後一條
cm = cmap_of(1)
n = len(ZI[0])
t = ZI[0][-1][0]
mk = '好作下'
if mk in t:
    fp = os.path.join(B, 'AI語譯', '_work', 'pian_manual', '篇01.json')
    m = json.load(io.open(fp, encoding='utf-8-sig')) if os.path.exists(fp) else {'splits': []}
    m['splits'] = [e for e in m.get('splits', []) if int(e['n']) != n]
    c = cm.get(n, 1)
    m['splits'].append({'n': n, 'base': max(1, c - 1), 'markers': [mk], 'targets': [max(1, c - 1), c]})
    json.dump(m, io.open(fp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('篇1 末記 已切', mk)
