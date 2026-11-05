
import io
p = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\_src\build_baihua.py'
s = io.open(p, encoding='utf-8').read()
old = "        pf.page_break_before = (not first); pf.keep_with_next = True"
new = "        pf.page_break_before = True; pf.keep_with_next = True"
assert s.count(old) == 1
s = s.replace(old, new)
old2 = "                pf.space_before = Pt(2 if mode == 'dui' else 6); pf.space_after = Pt(6)"
new2 = "                pf.space_before = Pt(5 if mode == 'dui' else 6); pf.space_after = Pt(8)"
assert s.count(old2) == 1
s = s.replace(old2, new2)
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
