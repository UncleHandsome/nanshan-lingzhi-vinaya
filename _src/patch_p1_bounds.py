import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\mk_pian_split.py'
s = io.open(p, encoding='utf-8').read()

# 1) 移除重複的十門清單區塊
start = s.find("    if p == 1:\n        MEN = [")
if start > 0:
    end = s.find("    if front:", start)
    s = s[:start] + s[end:]

# 2) 用 bounds_卷首.json 逐段配對
old_start = s.find("    if p == 1:\n        sp0 = [")
if old_start < 0:
    old_start = s.find("    if p == 1:\n        # 卷首")

# 找到下一個區塊起點（if front: 或 EMIT）
old_end = s.find("    if front:", old_start)
if old_end < 0:
    old_end = s.find("    EMIT = set()", old_start)

new = """    if p == 1:
        sp0 = [x.strip() for x in io.open(os.path.join(B, 'TXT_分卷', '01_行事鈔', '00_卷首.txt'), encoding='utf-8').read().split('\\n')[5:] if x.strip()]
        tt0 = [x.strip() for x in re.split(r'\\r?\\n\\r?\\n', io.open(os.path.join(B, 'AI語譯', 'out', '01_行事鈔', '00_卷首.txt'), encoding='utf-8').read()) if x.strip()]
        bz = []
        bfp = os.path.join(B, 'AI語譯', '_work', 'pian_bounds', 'bounds_卷首.json')
        if os.path.exists(bfp):
            dd = json.load(io.open(bfp, encoding='utf-8-sig'))
            bz = sorted((int(x['c']), int(x['n'])) for x in dd.get('bounds', []))
        starts = {c: n for c, n in bz}
        cvals = [c for c, n in bz]
        ptr = bz[0][1] if bz else 1
        for i, ct in enumerate(sp0):
            cno = i + 1
            qq = doc.add_paragraph(); qf = qq.paragraph_format
            qf.space_before = Pt(6); qf.space_after = Pt(1); qf.line_spacing = 1.2; qf.keep_with_next = True
            sr(qq.add_run('【鈔首%02d】' % cno + ct), 10, color=RGBColor(0x6b, 0x5b, 0x4a)); shade(qq, 'F4EFE2')
            if i < len(tt0):
                a2 = doc.add_paragraph(); a2.paragraph_format.first_line_indent = Pt(20)
                a2.paragraph_format.line_spacing = 1.3; a2.paragraph_format.space_after = Pt(2)
                sr(a2.add_run(clean_tr(tt0[i])), 10.5)
            if cno in starts:
                ptr = starts[cno]
            # 下一個 c 的起點
            nxts = [starts[x] for x in cvals if x > cno]
            nxt = min(nxts) if nxts else len(zi) + 1
            nxt = max(nxt, ptr)
            for k in range(ptr - 1, min(nxt - 1, len(zi))):
                emit_ji_tagged('【記%03d】' % (k + 1), clean(zi[k][0]), zi[k][1])
            ptr = nxt
        front = []

"""
s = s[:old_start] + new + s[old_end:]
io.open(p, 'w', encoding='utf-8').write(s)
print('p1 bounds-based interleave')
