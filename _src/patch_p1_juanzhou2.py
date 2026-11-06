import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\mk_pian_split.py'
s = io.open(p, encoding='utf-8').read()

start = s.find("    if front and p == 1:")
end = s.find("    if front:\n        q = doc.add_paragraph()", start)
assert start > 0 and end > start

new = """    if front and p == 1:
        # 卷首（序與十門）逐段列出，front 記按長度比例分配其下
        sp0 = [x.strip() for x in io.open(os.path.join(B, 'TXT_分卷', '01_行事鈔', '00_卷首.txt'), encoding='utf-8').read().split('\\n')[5:] if x.strip()]
        tt0 = [x.strip() for x in re.split(r'\\r?\\n\\r?\\n', io.open(os.path.join(B, 'AI語譯', 'out', '01_行事鈔', '00_卷首.txt'), encoding='utf-8').read()) if x.strip()]
        fl = list(front)
        tot = sum(max(1, len(re.findall(r'[\\u4e00-\\u9fff]', t))) for t in sp0) or 1
        acc = 0
        st = 0
        for i, ct in enumerate(sp0):
            qq = doc.add_paragraph(); qf = qq.paragraph_format
            qf.space_before = Pt(8); qf.space_after = Pt(1); qf.line_spacing = 1.25; qf.keep_with_next = True
            sr(qq.add_run('【鈔首%02d】' % (7 + i) + ct), 10, color=RGBColor(0x6b, 0x5b, 0x4a)); shade(qq, 'F4EFE2')
            if i < len(tt0):
                a2 = doc.add_paragraph(); a2.paragraph_format.first_line_indent = Pt(20)
                a2.paragraph_format.line_spacing = 1.3; a2.paragraph_format.space_after = Pt(2)
                sr(a2.add_run(clean_tr(tt0[i])), 10.5)
            acc += max(1, len(re.findall(r'[\\u4e00-\\u9fff]', ct)))
            nx = int(round(len(fl) * acc / tot)) if i < len(sp0) - 1 else len(fl)
            for k in fl[st:nx]:
                emit_ji_tagged('【記%03d】' % (k + 1), clean(zi[k][0]), zi[k][1])
            st = nx
        front = []

"""
s = s[:start] + new + s[end:]
io.open(p, 'w', encoding='utf-8').write(s)
print('p1 卷首 interleave v2')
