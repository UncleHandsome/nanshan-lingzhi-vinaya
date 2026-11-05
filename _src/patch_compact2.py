
import io
p = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\_src\build_baihua.py'
s = io.open(p, encoding='utf-8').read()
old = "        pf = p.paragraph_format; pf.first_line_indent = Pt(24); pf.line_spacing = 1.6; pf.space_after = Pt(4)"
new = "        pf = p.paragraph_format; pf.first_line_indent = Pt(20); pf.line_spacing = 1.4; pf.space_after = Pt(2)"
assert s.count(old) == 1
s = s.replace(old, new)
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
