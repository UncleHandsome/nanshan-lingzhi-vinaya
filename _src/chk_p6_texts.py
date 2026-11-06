import io, os, importlib.util

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ex)
zi = ex.build_zi(ex.sections(), ex.zsecs())[5]
for n in [15, 16, 21, 22, 24, 26, 27, 29, 31, 33, 47, 67, 76, 81, 88, 95]:
    print('=== 記%d' % n)
    print(zi[n - 1][0][:170])
    print()
