import io, os, re, importlib.util

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ex)
ZI = ex.build_zi(ex.sections(), ex.zsecs())
zi = ZI[5]
for n in [68, 85, 95, 98]:
    o = zi[n - 1][0]
    print('===== 記%d 長度%d' % (n, len(o)))
    print(o[:600])
    print()
