import io, os, json, importlib.util

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
CUTS = {
    84: (['明多少中'], [12, 13]),
    167: (['四發戒，標中'], [19, 20]),
    168: (['引文中，《俱舍》，初料'], [20, 22]),
    203: (['四戒相者，正當本篇'], [27, 28]),
    211: (['婬戒。〔佛在毘舍離國'], [28, 29]),
    230: (['不犯中三：初開無記', '盜戒'], [31, 32, 33]),
    314: (['六中。《伽論》所明'], [53, 54]),
    321: (['第二緣中。律有四句'], [57, 58]),
    453: (['十一。〔因前諫主'], [78, 79]),
    487: (['第二。〔佛在舍衛'], [88, 89]),
    488: (['釋第一中，初文', '二中。'], [89, 90, 91]),
    648: (['二十六。〔佛在羅閱祇'], [136, 137]),
    651: (['二十七。〔佛在舍衛'], [137, 138]),
    866: (['三十六。〔佛在舍衛'], [191, 192]),
    868: (['三十七。〔佛在羅閱城'], [192, 193]),
    942: (['四十九。〔六群有緣至軍中宿'], [219, 220]),
    943: (['五十。〔六群有緣在軍中觀鬪力'], [220, 221]),
    944: (['五十一。〔佛在支陀國'], [221, 222]),
    951: (['五十二。'], [222, 223]),
}
spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)
ZI = ex.build_zi(ex.sections(), ex.zsecs())[13]
N = len(ZI)

bs = [(int(x['c']), int(x['n'])) for x in json.load(io.open(os.path.join(B, 'AI語譯', '_work', 'pian_bounds', 'bounds_篇14.json'), encoding='utf-8-sig'))['bounds']]
base_cm = {}
for i, (c, n) in enumerate(bs):
    end = bs[i + 1][1] - 1 if i + 1 < len(bs) else 10 ** 6
    for k in range(n, max(n, end) + 1):
        base_cm[k] = c

cm, cur = {}, 1
for n in range(1, N + 1):
    if n in CUTS:
        tg = list(CUTS[n][1])
        if tg[0] < cur:
            shift = cur - tg[0]
            tg = [x + shift for x in tg]
        cm[n] = tg[0]
        cur = tg[-1]
    else:
        c = max(cur, base_cm.get(n, cur))
        cm[n] = c
        cur = c

bounds = {}
for n in range(1, N + 1):
    bounds.setdefault(cm[n], n)
out_bs = [{'c': c, 'n': bounds[c]} for c in sorted(bounds)]
json.dump({'bounds': out_bs}, io.open(os.path.join(B, 'AI語譯', '_work', 'pian_bounds', 'bounds_篇14.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

splits = []
for n, (marks, tg) in CUTS.items():
    tg = list(tg)
    base = tg[0]
    splits.append({'n': n, 'base': base, 'markers': marks, 'targets': tg,
                   **({'flex': True} if tg != list(range(base, base + len(tg))) else {})})
json.dump({'splits': splits}, io.open(os.path.join(B, 'AI語譯', '_work', 'pian_split_out', 'split_篇14.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('bounds', len(out_bs), 'max c', out_bs[-1]['c'], 'cmap1088', cm[N], 'splits', len(splits))
