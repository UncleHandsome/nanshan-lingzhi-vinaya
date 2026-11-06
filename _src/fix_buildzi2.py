# -*- coding: utf-8 -*-
import io, json, os, importlib.util

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\export_materials.py'
s = io.open(p, encoding='utf-8').read()
s = s.replace("if sn == nm or sn.startswith(nm) or nm.startswith(sn):",
              "if sn == nm or sn.startswith(nm) or nm.startswith(sn) or nm in sn:")
io.open(p, 'w', encoding='utf-8').write(s)
print('build_zi substring match')

spec = importlib.util.spec_from_file_location('ex', p)
ex = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ex)
ZI = ex.build_zi(ex.sections(), ex.zsecs())
print('counts', [len(ZI[i]) for i in range(11)])
zi0 = ZI[0]
off = None
for i, (o, t) in enumerate(zi0):
    if '古科列名' in o:
        off = i
        break
print('古科 index', off, 'ZI0', len(zi0))

# 舊 bounds 以 古科=1 編號，換算到新編號
if off is not None:
    fp = os.path.join(B, 'AI語譯', '_work', 'pian_bounds', 'bounds_卷首.json')
    d = json.load(io.open(fp, encoding='utf-8-sig'))
    for x in d['bounds']:
        x['n'] = int(x['n']) + off
    json.dump(d, io.open(fp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('bounds shifted by', off)
