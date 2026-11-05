
import io
p = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\_src\build_baihua.py'
s = io.open(p, encoding='utf-8').read()
reps = [
 ("sec.top_margin = Cm(2.3); sec.bottom_margin = Cm(2.0)", "sec.top_margin = Cm(1.7); sec.bottom_margin = Cm(1.6)"),
 ("sec.left_margin = Cm(2.2); sec.right_margin = Cm(2.2)", "sec.left_margin = Cm(1.8); sec.right_margin = Cm(1.8)"),
 ("ns.top_margin = Cm(2.3); ns.bottom_margin = Cm(2.0)", "ns.top_margin = Cm(1.7); ns.bottom_margin = Cm(1.6)"),
 ("ns.left_margin = Cm(2.2); ns.right_margin = Cm(2.2)", "ns.left_margin = Cm(1.8); ns.right_margin = Cm(1.8)"),
 ("    for _ in range(5):\n        p = doc.add_paragraph(); p.add_run(''); p.paragraph_format.space_after = Pt(0)",
  "    for _ in range(3):\n        p = doc.add_paragraph(); p.add_run(''); p.paragraph_format.space_after = Pt(0)",
 ),
 ("set_run(p.add_run('四分律刪繁補闕行事鈔'), 30, bold=True)", "set_run(p.add_run('四分律刪繁補闕行事鈔'), 26, bold=True)"),
 ("set_run(p.add_run('白話語譯' + ('‧對照本' if mode == 'dui' else '‧全白話本')), 18)",
  "set_run(p.add_run('白話語譯' + ('‧對照本' if mode == 'dui' else '‧全白話本')), 15)"),
 ("    p.paragraph_format.space_after = Pt(60)\n", "    p.paragraph_format.space_after = Pt(30)\n"),
 ("    p.paragraph_format.space_after = Pt(70)\n", "    p.paragraph_format.space_after = Pt(36)\n"),
 ("set_run(p.add_run('凡　例'), 18, bold=True)", "set_run(p.add_run('凡　例'), 16, bold=True)"),
 ("        pf.first_line_indent = Pt(24); pf.line_spacing = 1.6; pf.space_after = Pt(4)",
  "        pf.first_line_indent = Pt(20); pf.line_spacing = 1.4; pf.space_after = Pt(2)"),
 ("        set_run(p.add_run('【' + k + '】'), 10.5, bold=True)\n        set_run(p.add_run(v), 10.5)",
  "        set_run(p.add_run('【' + k + '】'), 9.5, bold=True)\n        set_run(p.add_run(v), 9.5)"),
 ("set_run(p.add_run('目　次'), 18, bold=True)", "set_run(p.add_run('目　次'), 16, bold=True)"),
 ("        set_run(p.add_run(a + '　'), 11, color=RGBColor(0x88, 0x88, 0x88))\n        set_run(p.add_run(b), 11)",
  "        set_run(p.add_run(a + '　'), 10, color=RGBColor(0x88, 0x88, 0x88))\n        set_run(p.add_run(b), 10)"),
 ("        pf.space_before = Pt(0); pf.space_after = Pt(6)\n        pf.page_break_before = True; pf.keep_with_next = True",
  "        pf.space_before = Pt(0); pf.space_after = Pt(4)\n        pf.page_break_before = True; pf.keep_with_next = True"),
 ("        set_run(p.add_run(meta['title']), 20, bold=True, color=RGBColor(0, 0, 0))",
  "        set_run(p.add_run(meta['title']), 16, bold=True, color=RGBColor(0, 0, 0))"),
 ("        set_run(p.add_run(meta['plain']), 11, color=RGBColor(0x88, 0x88, 0x88))",
  "        set_run(p.add_run(meta['plain']), 9.5, color=RGBColor(0x88, 0x88, 0x88))"),
 ("        p.paragraph_format.space_after = Pt(22)\n        set_run(p.add_run(meta['gloss']), 9.5, color=RGBColor(0xaa, 0xaa, 0xaa))",
  "        p.paragraph_format.space_after = Pt(12)\n        set_run(p.add_run(meta['gloss']), 8.5, color=RGBColor(0xaa, 0xaa, 0xaa))"),
 ("                pf = p.paragraph_format; pf.space_before = Pt(0); pf.space_after = Pt(0); pf.line_spacing = 1.35\n                set_run(p.add_run(raw.strip()), 10.5, color=RGBColor(0x66, 0x66, 0x66))",
  "                pf = p.paragraph_format; pf.space_before = Pt(0); pf.space_after = Pt(0); pf.line_spacing = 1.15\n                set_run(p.add_run(raw.strip()), 9, color=RGBColor(0x66, 0x66, 0x66))"),
 ("                pf.left_indent = Pt(8); pf.space_before = Pt(10); pf.space_after = Pt(2); pf.line_spacing = 1.3\n                set_run(p.add_run(raw), 10, color=RGBColor(0x6b, 0x5b, 0x4a))",
  "                pf.left_indent = Pt(6); pf.space_before = Pt(7); pf.space_after = Pt(0); pf.line_spacing = 1.2\n                set_run(p.add_run(raw), 8.5, color=RGBColor(0x6b, 0x5b, 0x4a))"),
 ("                pf.first_line_indent = Pt(22); pf.line_spacing = 1.7\n                pf.space_before = Pt(5 if mode == 'dui' else 6); pf.space_after = Pt(8)\n                set_run(p.add_run(tr), 11.5 if mode == 'qian' else 11)",
  "                pf.first_line_indent = Pt(19 if mode == 'dui' else 20)\n                pf.line_spacing = 1.35 if mode == 'dui' else 1.5\n                pf.space_before = Pt(3 if mode == 'dui' else 4); pf.space_after = Pt(5 if mode == 'dui' else 3)\n                set_run(p.add_run(tr), 10 if mode == 'qian' else 9.5)"),
 ("    set_run(hp.add_run('行事鈔白話' + ('（對照）' if mode == 'dui' else '')), 8.5, color=RGBColor(0xaa, 0xaa, 0xaa))",
  "    set_run(hp.add_run('行事鈔白話' + ('（對照）' if mode == 'dui' else '')), 8, color=RGBColor(0xaa, 0xaa, 0xaa))"),
 ("    set_run(fp.add_run('— '), 9.5, color=RGBColor(0x88, 0x88, 0x88))", "    set_run(fp.add_run('— '), 8.5, color=RGBColor(0x88, 0x88, 0x88))"),
 ("    fr = add_field(fp, ' PAGE '); fr.font.size = Pt(9.5); fr.font.color.rgb = RGBColor(0x88, 0x88, 0x88)",
  "    fr = add_field(fp, ' PAGE '); fr.font.size = Pt(8.5); fr.font.color.rgb = RGBColor(0x88, 0x88, 0x88)"),
 ("    set_run(fp.add_run(' —'), 9.5, color=RGBColor(0x88, 0x88, 0x88))", "    set_run(fp.add_run(' —'), 8.5, color=RGBColor(0x88, 0x88, 0x88))"),
]
miss = 0
for old, new in reps:
    n = s.count(old)
    if n == 0:
        miss += 1
        print('MISS:', old[:60].replace('\n','\\n'))
    s = s.replace(old, new)
io.open(p, 'w', encoding='utf-8').write(s)
print('done, misses', miss)
