import io, os, importlib.util, sys

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ex)
ZI = ex.build_zi(ex.sections(), ex.zsecs())
cases = {1: [253, 258, 261, 278, 287, 310, 311, 324],
         2: [26, 27, 34, 35, 44, 45],
         3: [7, 10, 11, 12, 13, 14, 35, 52, 53],
         4: [19, 20, 30, 49, 50],
         5: [38, 39, 52, 53, 54, 55, 73, 74]}
for p, ns in cases.items():
    print('######## 篇%d' % p)
    for n in ns:
        t = ZI[p - 1][n - 1][0]
        print('=== 記%d (%d字)' % (n, len(t)))
        print(t[:260])
