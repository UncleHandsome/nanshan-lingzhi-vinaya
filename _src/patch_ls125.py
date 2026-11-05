
import io
p = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\_src\build_user.py'
s = io.open(p, encoding='utf-8').read()
reps = [
 ("pf.space_before = Pt(2); pf.space_after = Pt(2); pf.line_spacing = 1.35",
  "pf.space_before = Pt(2); pf.space_after = Pt(2); pf.line_spacing = 1.25"),
 ("pf.space_before = Pt(2); pf.space_after = Pt(2); pf.line_spacing = 1.3",
  "pf.space_before = Pt(2); pf.space_after = Pt(2); pf.line_spacing = 1.25"),
]
for old, new in reps:
    print(s.count(old), old[-30:])
    s = s.replace(old, new)
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
