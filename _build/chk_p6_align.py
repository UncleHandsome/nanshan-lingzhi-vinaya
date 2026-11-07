import io, os, json, sys, importlib.util

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ex)
secs = ex.sections(); zs = ex.zsecs()
ZI = ex.build_zi(secs, zs)
am = json.load(io.open(os.path.join(B, 'AI語譯', '_work', 'hb_align.json'), encoding='utf-8'))

idx = 5  # 篇6
print('篇6 鈔段前 4：')
for i, (o, t) in enumerate(secs[idx]['items'][:4], 1):
    print('  鈔%d: %s' % (i, o[:40]))
print('\n篇6 記段前 12 的對應鈔號：', am[str(idx)][:12])
print('\n記段內容：')
for i, (o, t) in enumerate(ZI[idx][:12], 1):
    print('  記%d → 鈔%s : %s' % (i, am[str(idx)][i - 1], o[:38]))
