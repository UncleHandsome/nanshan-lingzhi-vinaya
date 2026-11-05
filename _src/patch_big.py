
import io
p = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\_src\build_baihua.py'
s = io.open(p, encoding='utf-8').read()
reps = [
 ("set_run(p.add_run(raw), 8.5, color=RGBColor(0x6b, 0x5b, 0x4a))",
  "set_run(p.add_run(raw), 10.5, color=RGBColor(0x6b, 0x5b, 0x4a))"),
 ("pf.first_line_indent = Pt(19 if mode == 'dui' else 20)",
  "pf.first_line_indent = Pt(23 if mode == 'dui' else 24)"),
 ("set_run(p.add_run(tr), 10 if mode == 'qian' else 9.5)",
  "set_run(p.add_run(tr), 12 if mode == 'qian' else 11.5)"),
 ("set_run(p.add_run(raw.strip()), 9, color=RGBColor(0x66, 0x66, 0x66))",
  "set_run(p.add_run(raw.strip()), 10, color=RGBColor(0x66, 0x66, 0x66))"),
 ("set_run(p.add_run('【' + k + '】'), 9.5, bold=True)\n        set_run(p.add_run(v), 9.5)",
  "set_run(p.add_run('【' + k + '】'), 10.5, bold=True)\n        set_run(p.add_run(v), 10.5)"),
 ("set_run(p.add_run(meta['title']), 16, bold=True, color=RGBColor(0, 0, 0))",
  "set_run(p.add_run(meta['title']), 17, bold=True, color=RGBColor(0, 0, 0))"),
 ("set_run(p.add_run(meta['plain']), 9.5, color=RGBColor(0x88, 0x88, 0x88))",
  "set_run(p.add_run(meta['plain']), 10, color=RGBColor(0x88, 0x88, 0x88))"),
 ("set_run(p.add_run(meta['gloss']), 8.5, color=RGBColor(0xaa, 0xaa, 0xaa))",
  "set_run(p.add_run(meta['gloss']), 9, color=RGBColor(0xaa, 0xaa, 0xaa))"),
]
for old, new in reps:
    n = s.count(old)
    if n != 1:
        print('COUNT', n, old[:50])
    s = s.replace(old, new)
io.open(p, 'w', encoding='utf-8').write(s)
print('patched')
