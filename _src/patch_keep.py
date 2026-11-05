
import io
p = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\_src\build_baihua.py'
s = io.open(p, encoding='utf-8').read()
old = "                pf.left_indent = Pt(6); pf.space_before = Pt(7); pf.space_after = Pt(0); pf.line_spacing = 1.2"
new = "                pf.left_indent = Pt(6); pf.space_before = Pt(7); pf.space_after = Pt(0); pf.line_spacing = 1.2; pf.keep_with_next = True"
assert s.count(old) == 1
s = s.replace(old, new)
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
