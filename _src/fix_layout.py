
import io
p = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\_src\build_vol.py'
s = io.open(p, encoding='utf-8').read()
# 1) always read translation from out/
old1 = """        if key.startswith('01a_'):
            tr = io.open(os.path.join(WORK, '01a_pass1.txt'), encoding='utf-8').read()
        else:
            tr = io.open(os.path.join(TR, key + '.txt'), encoding='utf-8').read()"""
new1 = """        tr = io.open(os.path.join(TR, key + '.txt'), encoding='utf-8').read()"""
assert s.count(old1) == 1
s = s.replace(old1, new1)
# 2) drop CBETA index lines from source
old2 = "        sp = [x.strip() for x in src if x.strip()]"
new2 = "        sp = [x.strip() for x in src if x.strip() and not re.match(r'^\\d+\\s+.*篇\\([上中下][一二三四]\\)$', x.strip())]"
assert s.count(old2) == 1
s = s.replace(old2, new2)
# 3) left-align short paragraphs (avoid justify spreading)
s = s.replace("                a = doc.add_paragraph(); a.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY\n                af = a.paragraph_format; af.first_line_indent = Pt(24); af.line_spacing = 1.25; af.space_before = Pt(2); af.space_after = Pt(4)\n                set_run(a.add_run(tp[i]), 12)",
              "                a = doc.add_paragraph(); a.alignment = WD_ALIGN_PARAGRAPH.LEFT if len(tp[i]) < 40 else WD_ALIGN_PARAGRAPH.JUSTIFY\n                af = a.paragraph_format; af.first_line_indent = Pt(24); af.line_spacing = 1.25; af.space_before = Pt(2); af.space_after = Pt(4)\n                set_run(a.add_run(tp[i]), 12)")
io.open(p, 'w', encoding='utf-8').write(s)
print('patched', s.count('LEFT if len(tp[i])'))
