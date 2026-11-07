import io, json, os, importlib.util

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
mp = os.path.join(B, 'AI語譯', '_work', 'pian_manual', '篇18.json')
m = {'splits': []}
if os.path.exists(mp):
    m = json.load(io.open(mp, encoding='utf-8-sig'))
add = [
    {'n': 18, 'base': 5, 'markers': ['七日藥中，初科'], 'targets': [5, 6]},
    {'n': 28, 'base': 7, 'markers': ['六味，標中'], 'targets': [7, 8]},
]
nums = {x['n'] for x in add}
m['splits'] = [e for e in m.get('splits', []) if int(e['n']) not in nums] + add
json.dump(m, io.open(mp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)
ZI = ex.build_zi(ex.sections(), ex.zsecs())[17]
for e in add:
    t = ZI[e['n'] - 1][0]
    for mk in e['markers']:
        print(e['n'], 'OK' if mk in t else 'MISS', mk)
