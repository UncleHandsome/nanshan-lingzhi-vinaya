import io, os, json, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'

# 1) 篇2 鈔18 以後整體後移一格（記052 屬鈔17）
fp = os.path.join(B, 'AI語譯', '_work', 'pian_bounds', 'bounds_篇02.json')
d = json.load(io.open(fp, encoding='utf-8-sig'))
bs = d['bounds']
mx = 60
for x in bs:
    if x['c'] >= 18:
        x['n'] = min(mx, x['n'] + 1)
json.dump(d, io.open(fp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('篇2 bounds shifted:', [(x['c'], x['n']) for x in bs if x['c'] >= 18][:4], '...')

# 2) builder：頭部切分限前 60 字；含「釋結界篇」的頭不補到前篇
p = os.path.join(B, '_src', 'mk_pian_split.py')
s = io.open(p, encoding='utf-8').read()
s = s.replace("    if _m and _m.start() > 4:", "    if _m and 4 < _m.start() < 60:")
s = s.replace("""    for p, (head, htr) in HEADS.items():""",
"""    for p, (head, htr) in HEADS.items():
        if '釋結界篇' in head or '資持記上二' in head:
            continue""")
io.open(p, 'w', encoding='utf-8').write(s)
print('builder guards updated')
