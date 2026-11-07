import io, json, os

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\mk_pian_split.py'
s = io.open(p, encoding='utf-8').read()

s = s.replace('for _p in range(2, 11):', 'for _p in range(2, len(SECS)):')

old = "    chao = [it for it in sec['items'] if not SKIP.match(it[0].strip())]"
new = """    chao = [it for it in sec['items'] if not SKIP.match(it[0].strip())]
    if p == 30:
        chao = chao[42:]
        am = [max(1, int(x) - 42) if int(x) > 0 else 0 for x in am]"""
assert old in s
s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8').write(s)
print('builder patched')

bp = os.path.join(B, 'AI語譯', '_work', 'pian_bounds', 'bounds_篇14.json')
d = json.load(io.open(bp, encoding='utf-8-sig'))
for x in d['bounds']:
    x['n'] = int(x['n']) + 1
json.dump(d, io.open(bp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('篇14 bounds +1')
