import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\mk_pian_split.py'
s = io.open(p, encoding='utf-8').read()
old = "if p != 10 and 'base' not in e and not e.get('flex'):"
new = "if p != 10 and (p == 14 or 'base' not in e) and not e.get('flex'):"
assert old in s
s = s.replace(old, new)
io.open(p, 'w', encoding='utf-8').write(s)
print('guard patched')
