import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\mk_pian_split.py'
s = io.open(p, encoding='utf-8').read()

# 記錄每段切幾片
s = s.replace("""    pieces = {}
    used = set()""", """    pieces = {}
    used = set()
    PARTS = {}""")
s = s.replace("""        for part, tr, c in zip(parts, ts, tg):
            pieces.setdefault(c, []).append((n, part, tr))
            used.add(n)""", """        PARTS[n] = len(tg)
        for idx2, (part, tr, c) in enumerate(zip(parts, ts, tg)):
            pieces.setdefault(c, []).append((n, idx2, part, tr))
            used.add(n)""")
s = s.replace("""        rows = [(n, part, tr) for n, part, tr in pieces.get(cno, [])]""",
"""        rows = [(n, idx2, part, tr) for n, idx2, part, tr in pieces.get(cno, [])]""")
s = s.replace("""            if k + 1 not in used:
                rows.append((k + 1, zi[k][0], zi[k][1]))
                used.add(k + 1)
        for n, part, tr in sorted(rows, key=lambda x: x[0]):
            emit_ji(n, clean(part), tr)""",
"""            if k + 1 not in used:
                rows.append((k + 1, 0, zi[k][0], zi[k][1]))
                used.add(k + 1)
        for n, idx2, part, tr in sorted(rows, key=lambda x: (x[0], x[1])):
            tot = PARTS.get(n, 1)
            if tot > 1:
                sub = ['前半', '後半'] if tot == 2 else (['前', '中', '後'] if tot == 3 else ['一', '二', '三', '四', '五'][:tot])
                tag = '【記%03d】（%s）' % (n, sub[idx2] if idx2 < len(sub) else str(idx2 + 1))
            else:
                tag = '【記%03d】' % n
            emit_ji_tagged(tag, clean(part), tr)""")
# emit_ji 改為帶標籤
s = s.replace("""    def emit_ji(n, zo, zt):
        r = doc.add_paragraph(); rf = r.paragraph_format
        rf.space_before = Pt(4); rf.space_after = Pt(1); rf.line_spacing = 1.2
        rf.left_indent = Pt(14); rf.keep_with_next = True
        sr(r.add_run('【記%03d】' % n + zo), 9.5, color=RGBColor(0x21, 0x5a, 0x8a)); shade(r, 'EEF2F6')""",
"""    def emit_ji_tagged(tag, zo, zt):
        r = doc.add_paragraph(); rf = r.paragraph_format
        rf.space_before = Pt(4); rf.space_after = Pt(1); rf.line_spacing = 1.2
        rf.left_indent = Pt(14); rf.keep_with_next = True
        sr(r.add_run(tag + zo), 9.5, color=RGBColor(0x21, 0x5a, 0x8a)); shade(r, 'EEF2F6')""")
s = s.replace("""            emit_ji(k + 1, zi[k][0], zi[k][1])""", """            emit_ji_tagged('【記%03d】' % (k + 1), clean(zi[k][0]), zi[k][1])""")
s = s.replace("""            emit_ji(k + 1, clean(zi[k][0]), zi[k][1])""", """            emit_ji_tagged('【記%03d】' % (k + 1), clean(zi[k][0]), zi[k][1])""")
io.open(p, 'w', encoding='utf-8').write(s)
print('part labels added')
