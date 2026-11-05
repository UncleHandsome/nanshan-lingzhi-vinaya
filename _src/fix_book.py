
import io
p = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\_src\build_book.py'
s = io.open(p, encoding='utf-8').read()

old = """        juan = key.split('_', 1)[1] if '_' in key else ''
        out.append(dict(key=key, juan=juan, src=sp, tr=tp))"""
new = """        juan = key.split('_', 1)[1] if '_' in key else ''
        keep = [i for i, x in enumerate(sp) if not re.match(r'^(No\\.\\d+|四分律刪補隨機羯磨疏卷|四分律行事鈔卷)', x)]
        if len(keep) != len(sp):
            sp = [sp[i] for i in keep]
            tp = [tp[i] for i in keep if i < len(tp)]
        out.append(dict(key=key, juan=juan, src=sp, tr=tp))"""
assert s.count(old) == 1
s = s.replace(old, new)

old2 = """            set_run(p.add_run(c['juan']), 17, bold=True)"""
new2 = """            set_run(p.add_run(title + '　' + c['juan']), 15, bold=True)"""
assert s.count(old2) == 1
s = s.replace(old2, new2)

# 短段落壓縮行距
old3 = """                q = doc.add_paragraph(); qf = q.paragraph_format
                qf.left_indent = Pt(6); qf.space_before = Pt(5); qf.space_after = Pt(0); qf.line_spacing = 1.2; qf.keep_with_next = True
                set_run(q.add_run(sp[i]), 10.5, color=RGBColor(0x6b,0x5b,0x4a)); shade(q, 'F7F3EA'); left_border(q, 'CDBC9C')
                a = doc.add_paragraph(); a.alignment = WD_ALIGN_PARAGRAPH.LEFT if len(tp[i]) < 40 else WD_ALIGN_PARAGRAPH.JUSTIFY
                af = a.paragraph_format; af.first_line_indent = Pt(24); af.line_spacing = 1.25; af.space_before = Pt(2); af.space_after = Pt(4)"""
new3 = """                short = len(sp[i]) < 20 and len(tp[i]) < 30
                q = doc.add_paragraph(); qf = q.paragraph_format
                qf.left_indent = Pt(6); qf.space_before = Pt(1 if short else 5); qf.space_after = Pt(0); qf.line_spacing = 1.2; qf.keep_with_next = True
                set_run(q.add_run(sp[i]), 10.5, color=RGBColor(0x6b,0x5b,0x4a)); shade(q, 'F7F3EA'); left_border(q, 'CDBC9C')
                a = doc.add_paragraph(); a.alignment = WD_ALIGN_PARAGRAPH.LEFT if len(tp[i]) < 40 else WD_ALIGN_PARAGRAPH.JUSTIFY
                af = a.paragraph_format; af.first_line_indent = Pt(24); af.line_spacing = 1.25; af.space_before = Pt(0 if short else 2); af.space_after = Pt(1 if short else 4)"""
assert s.count(old3) == 1
s = s.replace(old3, new3)
io.open(p, 'w', encoding='utf-8').write(s)
print('patched')
