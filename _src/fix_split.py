
import io
p = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\_src\split_all.py'
s = io.open(p, encoding='utf-8').read()
old = "            part2 = [label + '（續）'] + lines[k:]"
new = "            part2 = [label + '（續）'] + lines[k:j]"
assert s.count(old) == 1
s = s.replace(old, new)
io.open(p, 'w', encoding='utf-8').write(s)
print('fixed')
