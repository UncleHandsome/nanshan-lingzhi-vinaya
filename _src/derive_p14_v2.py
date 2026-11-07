import io, os, json, importlib.util

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)
ZI = ex.build_zi(ex.sections(), ex.zsecs())[13]
N = len(ZI)

SP = json.load(io.open(os.path.join(B, 'AI語譯', '_work', 'pian_split_out', 'split_篇14.json'), encoding='utf-8-sig'))['splits']
smap = {int(e['n']): e for e in SP}

cur = 1
cmap = {}
out_splits = []
for n in range(1, N + 1):
    e = smap.get(n)
    ok = False
    if e and 'markers' in e:
        o = ZI[n - 1][0]
        if all(m in o for m in e['markers']):
            k = len(e['markers']) + 1
            tg = list(range(cur, cur + k))
            cmap[n] = cur
            out_splits.append({'n': n, 'base': cur, 'markers': e['markers'], 'targets': tg})
            cur = tg[-1]
            ok = True
    if not ok:
        cmap[n] = cur

bounds = {}
for n in range(1, N + 1):
    bounds.setdefault(cmap[n], n)
bs = [{'c': c, 'n': bounds[c]} for c in sorted(bounds)]
json.dump({'bounds': bs}, io.open(os.path.join(B, 'AI語譯', '_work', 'pian_bounds', 'bounds_篇14.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump({'splits': out_splits}, io.open(os.path.join(B, 'AI語譯', '_work', 'pian_split_out', 'split_篇14.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('bounds', len(bs), 'c max', bs[-1]['c'], 'splits', len(out_splits))
