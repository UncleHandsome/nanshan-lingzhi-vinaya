import io, os, json, importlib.util

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
CUTS = [
    (84, ['明多少中'], [12, 13]),
    (167, ['四發戒，標中'], [19, 20]),
    (168, ['引文中，《俱舍》，初料'], [20, 22]),
    (203, ['四戒相者，正當本篇'], [27, 28]),
    (211, ['婬戒。〔佛在毘舍離國'], [28, 29]),
    (230, ['不犯中三：初開無記', '盜戒'], [31, 32, 33]),
    (314, ['六中。《伽論》所明'], [53, 54]),
    (321, ['第二緣中。律有四句'], [57, 58]),
    (453, ['十一。〔因前諫主'], [78, 79]),
    (487, ['第二。〔佛在舍衛'], [88, 89]),
    (488, ['釋第一中，初文', '二中。'], [89, 90, 91]),
    (648, ['二十六。〔佛在羅閱祇'], [136, 137]),
    (651, ['二十七。〔佛在舍衛'], [137, 138]),
    (866, ['三十六。〔佛在舍衛'], [191, 192]),
    (868, ['三十七。〔佛在羅閱城'], [192, 193]),
    (942, ['四十九。〔六群有緣至軍中宿'], [219, 220]),
    (943, ['五十。〔六群有緣在軍中觀鬪力'], [220, 221]),
    (944, ['五十一。〔佛在支陀國'], [221, 222]),
    (951, ['五十二。'], [222, 223]),
]
spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)
ZI = ex.build_zi(ex.sections(), ex.zsecs())[13]
arr = []
for n, marks, tg in CUTS:
    t = ZI[n - 1][0]
    ok = True
    for mk in marks:
        if mk not in t:
            print('MISS 記%d: %s' % (n, mk)); ok = False
    if ok:
        arr.append({'n': n, 'base': tg[0], 'markers': marks, 'targets': tg,
                    **({'flex': True} if tg != list(range(tg[0], tg[0] + len(tg))) else {})})
print('可用', len(arr), '/', len(CUTS))
fp = os.path.join(B, 'AI語譯', '_work', 'pian_manual', '篇14.json')
m = {'splits': []}
if os.path.exists(fp):
    m = json.load(io.open(fp, encoding='utf-8-sig'))
nums = {e['n'] for e in arr}
m['splits'] = [e for e in m.get('splits', []) if int(e['n']) not in nums] + arr
json.dump(m, io.open(fp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('已寫入 篇14 手動切點', len(m['splits']))
