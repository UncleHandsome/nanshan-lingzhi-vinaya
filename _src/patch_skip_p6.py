import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\mk_pian_split.py'
s = io.open(p, encoding='utf-8').read()
old = "def build(p, splits):\n    idx = p - 1"
new = ("def build(p, splits):\n"
       "    if p == 6:\n"
       "        print('篇6 使用精修版（mk_p6_huiben.py），此處跳過')\n"
       "        return\n"
       "    idx = p - 1")
assert old in s
s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8').write(s)
print('skip p6 patched')
