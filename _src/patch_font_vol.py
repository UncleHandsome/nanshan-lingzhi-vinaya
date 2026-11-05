
import io
p = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\_src\build_user.py'
s = io.open(p, encoding='utf-8').read()
reps = [
 ("            set_run(p.add_run(t), 9.5, color=RGBColor(0x6b, 0x5b, 0x4a))",
  "            set_run(p.add_run(t), 10.5, color=RGBColor(0x6b, 0x5b, 0x4a))"),
 ("    set_run(p.add_run('卷一（上之一）　序．標宗顯德篇．集僧通局篇'), 10.5, color=RGBColor(0x55, 0x55, 0x55))",
  "    set_run(p.add_run('上卷　序．標宗顯德篇．集僧通局篇（餘篇待續）'), 10.5, color=RGBColor(0x55, 0x55, 0x55))"),
 ("行事鈔_白話對照本_卷一_定本v2.docx", "行事鈔_白話對照本_上卷.docx"),
 ("行事鈔_全白話本_卷一_定本v2.docx", "行事鈔_全白話本_上卷.docx"),
]
for old, new in reps:
    c = s.count(old)
    print(c, old[:40])
    s = s.replace(old, new)
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
