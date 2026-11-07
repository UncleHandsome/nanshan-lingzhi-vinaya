import io, os, json, importlib.util

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)
ZI = ex.build_zi(ex.sections(), ex.zsecs())[13]
N = len(ZI)

# 讓這些記段落回到其對應鈔號（修正記文跑到鈔文前的倒置）
ANCHOR = {537: 111, 544: 112, 750: 152, 761: 153, 977: 233, 979: 234}

bs = [(int(x['c']), int(x['n'])) for x in json.load(io.open(os.path.join(B, 'AI語譯', '_work', 'pian_bounds', 'bounds_篇14.json'), encoding='utf-8-sig'))['bounds']]
base_cm = {}
for i, (c, n) in enumerate(bs):
    end = bs[i + 1][1] - 1 if i + 1 < len(bs) else 10 ** 6
    for k in range(n, max(n, end) + 1):
        base_cm[k] = c

cm, cur = {}, 1
for n in range(1, N + 1):
    c = base_cm.get(n, cur)
    if n in ANCHOR:
        c = ANCHOR[n]
    c = max(cur, c)
    cm[n] = c
    cur = c

bounds = {}
for n in range(1, N + 1):
    bounds.setdefault(cm[n], n)
out_bs = [{'c': c, 'n': bounds[c]} for c in sorted(bounds)]
json.dump({'bounds': out_bs}, io.open(os.path.join(B, 'AI語譯', '_work', 'pian_bounds', 'bounds_篇14.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('anchors', ANCHOR, 'bounds', len(out_bs), 'max', out_bs[-1]['c'])
