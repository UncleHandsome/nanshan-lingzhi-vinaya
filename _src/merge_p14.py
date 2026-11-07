import io, os, json, importlib.util

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
D = os.path.join(B, '會本材料_11-30', '篇14_重出')
dec = json.JSONDecoder()
bounds = {}
splits = {}
for i in range(1, 11):
    s = io.open(os.path.join(D, '%d.txt' % i), encoding='utf-8-sig').read()
    j = 0
    while j < len(s):
        while j < len(s) and s[j] in ' \r\n\t,，':
            j += 1
        if j >= len(s):
            break
        try:
            o, j = dec.raw_decode(s, j)
        except Exception:
            j += 1
            continue
        if not isinstance(o, dict):
            continue
        for x in o.get('bounds', []):
            bounds[int(x['c'])] = int(x['n'])
        for x in o.get('splits', []):
            splits[int(x['n'])] = x

bs = [{'c': c, 'n': bounds[c]} for c in sorted(bounds)]
json.dump({'bounds': bs}, io.open(os.path.join(B, 'AI語譯', '_work', 'pian_bounds', 'bounds_篇14.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
sp = [splits[n] for n in sorted(splits)]
json.dump({'splits': sp}, io.open(os.path.join(B, 'AI語譯', '_work', 'pian_split_out', 'split_篇14.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('bounds', len(bs), 'c', bs[0]['c'], bs[-1]['c'], 'splits', len(sp))

spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)
ZI = ex.build_zi(ex.sections(), ex.zsecs())[13]
bad = 0
for e in sp:
    t = ZI[int(e['n']) - 1][0]
    miss = [m for m in e['markers'] if m not in t]
    if miss:
        bad += 1
        if bad <= 5:
            print('MISS n=%d %s' % (int(e['n']), miss[:2]))
print('marker 缺失', bad, '/', len(sp))
