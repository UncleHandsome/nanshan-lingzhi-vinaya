import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\mk_pian_split.py'
s = io.open(p, encoding='utf-8').read()
s = s.replace("""        first_n = BS[0][1]
        for n3 in range(1, first_n):
            cmap[n3] = 1""",
"""        first_n = BS[0][1]
        fend = max([k + 1 for k in front], default=0)
        for n3 in range(fend + 1, first_n):
            cmap[n3] = 1""")
io.open(p, 'w', encoding='utf-8').write(s)
print('skip front in c1')
