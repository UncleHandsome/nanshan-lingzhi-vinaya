import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\mk_pian_split.py'
s = io.open(p, encoding='utf-8').read()
old = "emit_ji_to(d, '【記%03d】（續前篇）' % len(ZI[p - 2]), head, htr)"
new = "emit_ji_to(d, '【記（續前篇）】', head, htr)"
assert old in s, 'label line not found'
s = s.replace(old, new)
io.open(p, 'w', encoding='utf-8').write(s)
print('tail label fixed')
