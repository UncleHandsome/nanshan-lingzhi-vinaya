import io, json, os

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\mk_pian_split.py'
s = io.open(p, encoding='utf-8').read()

# 1) HEADS 擴到全部篇
s = s.replace('for _p in range(2, 11):', 'for _p in range(2, len(SECS)):')

# 2) 篇30：去掉開頭 42 條（卷首總序），並把 am 的鈔號平移到 1 起
old = """    idx = p - 1"""
new = """    idx = p - 1
    if p == 30:
        chao = chao[42:]
        am = [max(1, int(x) - 42) if int(x) > 0 else 0 for x in am]"""
if old in s:
    s = s.replace(old, new, 1)

io.open(p, 'w', encoding='utf-8').write(s)
print('builder patched (heads, p30)')

# 3) 篇14 bounds 全體 +1
bp = os.path.join(B, 'AI語譯', '_work', 'pian_bounds', 'bounds_篇14.json')
d = json.load(io.open(bp, encoding='utf-8-sig'))
for x in d['bounds']:
    x['n'] = int(x['n']) + 1
json.dump(d, io.open(bp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('篇14 bounds +1', len(d['bounds']))
