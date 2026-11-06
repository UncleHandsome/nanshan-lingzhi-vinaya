import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\mk_pian_split.py'
s = io.open(p, encoding='utf-8').read()

old = """        b2 = doc.add_paragraph(); b2.paragraph_format.first_line_indent = Pt(20)
        b2.paragraph_format.left_indent = Pt(14)
        b2.paragraph_format.line_spacing = 1.28; b2.paragraph_format.space_after = Pt(2)
        sr(b2.add_run(zt), 10)"""
new = """        _lead = ''
        _zt = zt
        while _zt[:1] in ('〕', '」', '）'):
            _lead += _zt[0]
            _zt = _zt[1:]
        if _lead and doc.paragraphs:
            doc.paragraphs[-1].add_run(_lead)
        b2 = doc.add_paragraph(); b2.paragraph_format.first_line_indent = Pt(20)
        b2.paragraph_format.left_indent = Pt(14)
        b2.paragraph_format.line_spacing = 1.28; b2.paragraph_format.space_after = Pt(2)
        sr(b2.add_run(_zt), 10)"""
assert old in s, 'emit block not found'
s = s.replace(old, new)
io.open(p, 'w', encoding='utf-8').write(s)
print('bracket reattach added')
