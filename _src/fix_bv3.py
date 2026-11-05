
import io
p = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\_src\build_vol.py'
s = io.open(p, encoding='utf-8').read()
start = s.find("        if mode == 'dui' and len(sp) == len(tp):")
end = s.find("    doc.save(path)")
assert start > 0 and end > start
block = """        if mode == 'dui':
            m = min(len(sp), len(tp))
            for i in range(m):
                q = doc.add_paragraph(); qf = q.paragraph_format
                qf.left_indent = Pt(6); qf.space_before = Pt(5); qf.space_after = Pt(0); qf.line_spacing = 1.2; qf.keep_with_next = True
                set_run(q.add_run(sp[i]), 10.5, color=RGBColor(0x6b, 0x5b, 0x4a)); shade(q, 'F7F3EA'); left_border(q, 'CDBC9C')
                a = doc.add_paragraph(); a.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                af = a.paragraph_format; af.first_line_indent = Pt(24); af.line_spacing = 1.25; af.space_before = Pt(2); af.space_after = Pt(4)
                set_run(a.add_run(tp[i]), 12)
            for t in sp[m:]:
                q = doc.add_paragraph(); qf = q.paragraph_format
                qf.left_indent = Pt(6); qf.space_before = Pt(4); qf.space_after = Pt(0); qf.line_spacing = 1.2
                set_run(q.add_run(t), 10.5, color=RGBColor(0x6b, 0x5b, 0x4a)); shade(q, 'F7F3EA'); left_border(q, 'CDBC9C')
            for t in tp[m:]:
                a = doc.add_paragraph(); a.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                af = a.paragraph_format; af.first_line_indent = Pt(24); af.line_spacing = 1.25; af.space_before = Pt(2); af.space_after = Pt(4)
                set_run(a.add_run(t), 12)
        else:
            for t in tp:
                a = doc.add_paragraph(); a.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                af = a.paragraph_format; af.first_line_indent = Pt(24); af.line_spacing = 1.3
                af.space_before = Pt(2); af.space_after = Pt(4)
                set_run(a.add_run(t), 12)
"""
s = s[:start] + block + s[end:]
io.open(p, 'w', encoding='utf-8').write(s)
print('patched')
