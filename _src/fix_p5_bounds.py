import io, os, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
# 1) 篇5 bounds：c18 起各 -1（依使用者批准的方案）
fp = os.path.join(B, 'AI語譯', '_work', 'pian_bounds', 'bounds_篇05.json')
d = json.load(io.open(fp, encoding='utf-8-sig'))
for x in d['bounds']:
    if x['c'] >= 18:
        x['n'] = x['n'] - 1
json.dump(d, io.open(fp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('篇5 bounds c18+ shifted -1')

# 2) 移除篇5 記52/53/54/56 的切點（改用 bounds 整體後移）
mp = os.path.join(B, 'AI語譯', '_work', 'pian_manual', '篇05.json')
m = json.load(io.open(mp, encoding='utf-8-sig'))
keep = [e for e in m['splits'] if int(e['n']) not in (52, 53, 54, 56)]
json.dump({'splits': keep}, io.open(mp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('篇5 manual splits kept:', [e['n'] for e in keep])
