import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\mk_pian_split.py'
s = io.open(p, encoding='utf-8').read()

old = "base = (int(e['base']) if ('base' in e and p != 14)"
new = "base = (int(e['base']) if 'base' in e"
assert old in s
s = s.replace(old, new, 1)

old2 = "if p != 10 and (p == 14 or 'base' not in e) and not e.get('flex'):"
new2 = "if p != 10 and (p == 14 and 'base' not in e) or (p not in (10, 14) and 'base' not in e) and not e.get('flex'):"
assert old2 in s
s = s.replace(old2, new2, 1)
io.open(p, 'w', encoding='utf-8').write(s)
print('p14 base/guard patched')
