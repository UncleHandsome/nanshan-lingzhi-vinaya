import io, os, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
fp = os.path.join(B, 'AI語譯', '_work', 'pian_bounds', 'bounds_篇09.json')
d = json.load(io.open(fp, encoding='utf-8-sig'))
want = {6: 16, 7: 18, 8: 19, 9: 20}
for x in d['bounds']:
    if x['c'] in want:
        x['n'] = want[x['c']]
json.dump(d, io.open(fp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print([(x['c'], x['n']) for x in d['bounds']][:10])

mp = os.path.join(B, 'AI語譯', '_work', 'pian_manual', '篇09.json')
m = json.load(io.open(mp, encoding='utf-8-sig'))
keep = [e for e in m['splits'] if int(e['n']) in (36, 37, 64)]
json.dump({'splits': keep}, io.open(mp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('kept moves:', [e['n'] for e in keep])
