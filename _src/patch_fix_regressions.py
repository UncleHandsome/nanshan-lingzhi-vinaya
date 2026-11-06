import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\mk_pian_split.py'
s = io.open(p, encoding='utf-8').read()

# 1) 搬移條目不應加入 used（否則原位置被跳過、新位置也不輸出）
s = s.replace("""            by_c.setdefault(int(e['base']), []).append(n0 - 1)
            used.add(n0)""",
"""            by_c.setdefault(int(e['base']), []).append(n0 - 1)""")

# 2) 首記切分：放寬到 120 字，且只排除真正的卷頭
s = s.replace("    if _m and 4 < _m.start() < 60:", "    if _m and 4 < _m.start() < 120:")
s = s.replace("        if '釋結界篇' in head or '資持記上' in head:",
              "        if '釋結界篇' in head or '資持記上二' in head:")
io.open(p, 'w', encoding='utf-8').write(s)
print('move/head fixes')
