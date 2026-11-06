import io, json, os

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\mk_pian_split.py'
s = io.open(p, encoding='utf-8').read()

# 1) flex：允許 targets 不連續（一記多鈔插入）
old = "        if p != 10 and tg != list(range(base, base + len(tg))):\n            continue"
new = "        if p != 10 and not e.get('flex') and tg != list(range(base, base + len(tg))):\n            continue"
assert old in s, 'validation not found'
s = s.replace(old, new)

# 2) flex 條目不受 nxt 上限限制
old2 = "        if p != 10 and 'base' not in e:"
new2 = "        if p != 10 and 'base' not in e and not e.get('flex'):"
assert old2 in s
s = s.replace(old2, new2)

# 3) 標題尾端殘留 〕 清掉
old3 = "        sr(r.add_run(tag + zo), 9.5, color=RGBColor(0x21, 0x5a, 0x8a)); shade(r, 'EEF2F6')"
new3 = "        sr(r.add_run(tag + zo.rstrip('〕')), 9.5, color=RGBColor(0x21, 0x5a, 0x8a)); shade(r, 'EEF2F6')"
if old3 in s:
    s = s.replace(old3, new3)

io.open(p, 'w', encoding='utf-8').write(s)
print('flex support + tag rstrip')

# 4) 篇7 記7 flex 切點；bounds c2=8, c3=9
mp = os.path.join(B, 'AI語譯', '_work', 'pian_manual', '篇07.json')
m = json.load(io.open(mp, encoding='utf-8-sig'))
m['splits'] = [e for e in m['splits'] if int(e['n']) != 7]
m['splits'].append({'n': 7, 'base': 1, 'markers': ['化教，標中。'], 'targets': [1, 3], 'flex': True})
json.dump(m, io.open(mp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

bp = os.path.join(B, 'AI語譯', '_work', 'pian_bounds', 'bounds_篇07.json')
b = json.load(io.open(bp, encoding='utf-8-sig'))
for x in b['bounds']:
    if x['c'] == 2:
        x['n'] = 8
    if x['c'] == 3:
        x['n'] = 9
json.dump(b, io.open(bp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('篇7 記7 flex + bounds c2/c3')

specp = os.path.join(B, '_src', 'export_materials.py')
import importlib.util
spec = importlib.util.spec_from_file_location('ex', specp)
ex = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ex)
zi = ex.build_zi(ex.sections(), ex.zsecs())[6]
print('記7 marker:', '化教，標中。' in zi[6][0])
