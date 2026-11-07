import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\mk_pian_split.py'
s = io.open(p, encoding='utf-8').read()
old = "for _p in range(2, len(SECS)):"
new = "for _p in range(2, 2):  # 停用跨篇頭部搬移：篇題與記001 留在本篇"
assert old in s
s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8').write(s)
print('HEADS 搬移已停用')
