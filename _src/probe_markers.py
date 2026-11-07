import importlib.util, os

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)
ZI = ex.build_zi(ex.sections(), ex.zsecs())
cases = {18: [52, 75, 98, 102, 115], 19: [34, 40], 11: [57, 113]}
for p, ns in cases.items():
    print('#### 篇', p)
    for n in ns:
        if n <= len(ZI[p - 1]):
            t = ZI[p - 1][n - 1][0]
            print('=== 記%d (%d字)' % (n, len(t)))
            print(t[:300])
