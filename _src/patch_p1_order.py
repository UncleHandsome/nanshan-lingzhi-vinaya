import io, json, os

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'

# 1) 卷首 bounds 依使用者裁定
fp = os.path.join(B, 'AI語譯', '_work', 'pian_bounds', 'bounds_卷首.json')
d = json.load(io.open(fp, encoding='utf-8-sig'))
new = {3: 48, 4: 48, 5: 51, 6: 78, 7: 87, 8: 93, 9: 113, 10: 117, 11: 121, 40: 121, 41: 126, 64: 260, 71: 284}
for x in d['bounds']:
    if x['c'] in new:
        x['n'] = new[x['c']]
json.dump(d, io.open(fp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('bounds updated')

# 2) 續前篇標籤恢復編號
p = os.path.join(B, '_src', 'mk_pian_split.py')
s = io.open(p, encoding='utf-8').read()
old = "emit_ji_to(d, '【記（續前篇）】', head, htr)"
new_line = "emit_ji_to(d, '【記%03d】（續前篇）' % (len(ZI[p - 2]) + 1), head, htr)"
assert old in s, 'label not found'
s = s.replace(old, new_line)
io.open(p, 'w', encoding='utf-8').write(s)
print('label numbered')
