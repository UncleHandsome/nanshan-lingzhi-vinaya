import io, json, os, importlib.util

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
D = os.path.join(B, 'AI語譯', '_work', 'pian_manual')
ADD = {
    18: [
        {'n': 52, 'base': 19, 'markers': ['第三護淨'], 'targets': [19, 20]},
        {'n': 75, 'base': 31, 'markers': ['對顯中，內宿，對處'], 'targets': [31, 33], 'flex': True},
        {'n': 98, 'base': 55, 'markers': ['能授四法', '三中五過'], 'targets': [55, 56, 57]},
        {'n': 102, 'base': 57, 'markers': ['正加中', '盡形中四'], 'targets': [57, 58, 59]},
        {'n': 115, 'base': 69},
    ],
    19: [
        {'n': 34, 'base': 20, 'markers': ['第八中，初引《增一》'], 'targets': [20, 21]},
        {'n': 40, 'base': 28, 'markers': ['三中，《僧祇》'], 'targets': [28, 29]},
    ],
    11: [
        {'n': 57, 'base': 12, 'markers': ['四遇緣中'], 'targets': [12, 13]},
        {'n': 113, 'base': 39, 'markers': ['立法中，通標四家'], 'targets': [39, 40]},
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
        if 'markers' not in e:
            print('篇%d 搬移 記%d → 鈔%d' % (p, e['n'], e['base']))
            continue
        t = ZI[p - 1][e['n'] - 1][0]
        for mk in e['markers']:
            print('篇%d 記%d %s %s' % (p, e['n'], 'OK ' if mk in t else 'MISS', mk))
