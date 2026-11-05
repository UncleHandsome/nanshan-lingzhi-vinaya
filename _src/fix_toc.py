
import io
p = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\_src\build_vol.py'
s = io.open(p, encoding='utf-8').read()
old = """        if mode == 'dui':
            m = min(len(sp), len(tp))
            for i in range(m):"""
new = """        if mode == 'dui':
            m = min(len(sp), len(tp))
            for i in range(m):
                if re.match(r'^[\\u4e00-\\u9fff]{2,10}篇第[\\u4e00-\\u9fff]+$', sp[i]) and sp[i] == tp[i]:
                    q = doc.add_paragraph(); q.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    qf = q.paragraph_format; qf.space_before = Pt(1); qf.space_after = Pt(1); qf.line_spacing = 1.2
                    set_run(q.add_run(sp[i]), 10.5, color=RGBColor(0x55, 0x55, 0x55))
                    continue"""
assert s.count(old) == 1
s = s.replace(old, new)
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
