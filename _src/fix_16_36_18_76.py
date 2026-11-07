import io, os, json, importlib.util

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
D = os.path.join(B, 'AI語譯', '_work', 'pian_manual')
ADD = {
    16: [{'n': 36, 'base': 4, 'markers': ['次明制懺'], 'targets': [4, 5]}],
    18: [{'n': 76, 'base': 33, 'markers': ['內煮中。對處唯大'], 'targets': [33, 34]}],
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
        print(p, e['n'], [('OK' if mk in t else 'MISS') for mk in e['markers']])
