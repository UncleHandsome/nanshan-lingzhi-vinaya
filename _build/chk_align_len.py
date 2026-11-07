import io, os, json, sys, importlib.util

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ex)
secs = ex.sections(); zs = ex.zsecs()
ZI = ex.build_zi(secs, zs)
am = json.load(io.open(os.path.join(B, 'AI語譯', '_work', 'hb_align.json'), encoding='utf-8'))

print('篇  對齊表長度  記段數  狀態')
bad = 0
for i in range(len(secs)):
    a = am.get(str(i), [])
    n = len(ZI.get(i, []))
    ok = (len(a) == n)
    if not ok:
        bad += 1
    print('%-3d %8d %8d  %s' % (i + 1, len(a), n, '' if ok else '  <<< 不符'))
print('不符篇數', bad)
