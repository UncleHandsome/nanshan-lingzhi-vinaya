import io, os, json, importlib.util

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)
ZI = ex.build_zi(ex.sections(), ex.zsecs())

SPECS = {
    30: [
        {'n': 6, 'markers': ['釋中'], 'targets': [1, 2]},
        {'n': 11, 'markers': ['第四', '第二門'], 'targets': [4, 5, 6]},
        {'n': 16, 'markers': ['第四門', '《十誦》'], 'targets': [7, 8, 10]},
        {'n': 19, 'markers': ['《僧祇》', '《十誦》', '結中', '六中'], 'targets': [13, 14, 15, 16, 17]},
    ],
    5: [
        {'n': 80, 'markers': ['問互作中'], 'targets': [33, 34]},
        {'n': 81, 'markers': ['第三問'], 'targets': [34, 35]},
    ],
    8: [
        {'n': 108, 'move': 30},
        {'n': 109, 'markers': ['次辨遮中'], 'targets': [30, 31]},
    ],
    7: [
        {'n': 17, 'markers': ['《涅槃》中。'], 'targets': [17, 18]},
        {'n': 23, 'markers': ['治法中', '初訶責法'], 'targets': [21, 22, 23]},
    ],
    27: [
        {'n': 41, 'markers': ['次科', '第七'], 'targets': [40, 41, 42]},
    ],
}

for p, arr in SPECS.items():
    fp = os.path.join(B, 'AI語譯', '_work', 'pian_manual', '篇%02d.json' % p)
    m = json.load(io.open(fp, encoding='utf-8-sig')) if os.path.exists(fp) else {'splits': []}
    nums = {e['n'] for e in arr}
    m['splits'] = [e for e in m.get('splits', []) if int(e['n']) not in nums]
    for e in arr:
        n = e['n']
        t = ZI[p - 1][n - 1][0]
        if 'move' in e:
            m['splits'].append({'n': n, 'base': e['move']})
            print('篇%d 記%d 整條→鈔%d' % (p, n, e['move']))
            continue
        miss = [mk for mk in e['markers'] if mk not in t]
        if miss:
            print('MISS', p, n, miss); continue
        tg = e['targets']
        entry = {'n': n, 'base': tg[0], 'markers': e['markers'], 'targets': tg}
        if tg != list(range(tg[0], tg[0] + len(tg))):
            entry['flex'] = True
        m['splits'].append(entry)
        print('篇%d 記%d %s → %s' % (p, n, e['markers'], tg))
    json.dump(m, io.open(fp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
