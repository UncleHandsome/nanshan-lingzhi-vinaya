import io, json, os, importlib.util

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
D = os.path.join(B, 'AI語譯', '_work', 'pian_manual')
ADD = {
    11: [
        {'n': 36, 'base': 8, 'markers': ['分房法中。三時分易'], 'targets': [8, 9]},
        {'n': 105, 'base': 34, 'markers': ['事訖中'], 'targets': [34, 35]},
        {'n': 92, 'base': 29, 'markers': ['懸受者，謂前事如法'], 'targets': [29, 30]},
        {'n': 93, 'base': 30, 'markers': ['互用，正明中'], 'targets': [30, 31]},
    ],
    12: [
        {'n': 84, 'base': 23, 'markers': ['捨法中'], 'targets': [23, 24]},
    ],
    15: [
        {'n': 74, 'base': 26, 'markers': ['六明優劣'], 'targets': [26, 27]},
        {'n': 163, 'base': 64, 'markers': ['三明具緣'], 'targets': [64, 65]},
    ],
    18: [
        {'n': 3, 'base': 1, 'markers': ['時藥中，《四分》'], 'targets': [1, 4], 'flex': True},
        {'n': 56, 'base': 21, 'markers': ['問中。欲彰聖意'], 'targets': [21, 22]},
    ],
}
for p, arr in ADD.items():
    fp = os.path.join(D, '篇%02d.json' % p)
    m = {'splits': []}
    if os.path.exists(fp):
        m = json.load(io.open(fp, encoding='utf-8-sig'))
    nums = {int(x['n']) for x in arr}
    m['splits'] = [e for e in m.get('splits', []) if int(e['n']) not in nums] + arr
    json.dump(m, io.open(fp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)
ZI = ex.build_zi(ex.sections(), ex.zsecs())
for p, arr in ADD.items():
    for e in arr:
        t = ZI[p - 1][e['n'] - 1][0]
        for mk in e['markers']:
            print('篇%d 記%d %s %s' % (p, e['n'], 'OK ' if mk in t else 'MISS', mk))
