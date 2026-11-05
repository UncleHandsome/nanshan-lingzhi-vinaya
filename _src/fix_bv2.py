
import io
p = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\_src\build_vol.py'
s = io.open(p, encoding='utf-8').read()
old = """            if mode == 'dui':
                q = doc.add_paragraph(); qf = q.paragraph_format
                qf.left_indent = Pt(6); qf.space_before = Pt(5); qf.space_after = Pt(0); qf.line_spacing = 1.2
                set_run(q.add_run('　'.join(sp)), 10.5, color=RGBColor(0x6b, 0x5b, 0x4a)); shade(q, 'F7F3EA'); left_border(q, 'CDBC9C')"""
new = """            if mode == 'dui':
                for t in sp:
                    q = doc.add_paragraph(); qf = q.paragraph_format
                    qf.left_indent = Pt(6); qf.space_before = Pt(4); qf.space_after = Pt(0); qf.line_spacing = 1.2
                    set_run(q.add_run(t), 10.5, color=RGBColor(0x6b, 0x5b, 0x4a)); shade(q, 'F7F3EA'); left_border(q, 'CDBC9C')"""
assert s.count(old) == 1
s = s.replace(old, new)
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
