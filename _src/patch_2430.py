import io, json, os

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\mk_pian_split.py'
s = io.open(p, encoding='utf-8').read()

old = """    if p == 30:
        chao = chao[42:]
        am = [max(1, int(x) - 42) if int(x) > 0 else 0 for x in am]"""
new = """    if p == 30:
        chao = chao[42:]
        am = [max(1, min(23, int(x) - 42)) if int(x) > 42 else (23 if int(x) > 0 else 0) for x in am]
        for _k in range(24, min(28, len(am))):
            am[_k] = 23"""
assert old in s
s = s.replace(old, new)
io.open(p, 'w', encoding='utf-8').write(s)
print('p30 tail mapping')

# 篇24：記24 搬回鈔11，鈔12 起首改記25
mp = os.path.join(B, 'AI語譯', '_work', 'pian_manual', '篇24.json')
m = {'splits': []}
if os.path.exists(mp):
    m = json.load(io.open(mp, encoding='utf-8-sig'))
m['splits'] = [e for e in m.get('splits', []) if int(e['n']) != 24]
m['splits'].append({'n': 24, 'base': 11})
json.dump(m, io.open(mp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

bp = os.path.join(B, 'AI語譯', '_work', 'pian_bounds', 'bounds_篇24.json')
if os.path.exists(bp):
    b = json.load(io.open(bp, encoding='utf-8-sig'))
    for x in b['bounds']:
        if x['c'] == 12:
            x['n'] = 25
    json.dump(b, io.open(bp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('p24 adjusted')
