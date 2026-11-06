import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\mk_pian_split.py'
s = io.open(p, encoding='utf-8').read()

# A. 模組載入時切出各篇首記的前篇尾巴
s = s.replace("""SKIP = re.compile(r'^\\d+\\s*[\\u4e00-\\u9fff]{2,10}篇')""",
"""SKIP = re.compile(r'^\\d+\\s*[\\u4e00-\\u9fff]{2,10}篇')
HDR = re.compile(r'(\\d*\\s*釋[\\u4e00-\\u9fff]{1,6}篇(?:\\([^)）]*\\))?)')
HEADS = {}
for _p in range(2, 11):
    _o, _t = ZI[_p - 1][0]
    _m = HDR.search(_o[:160])
    if _m and _m.start() > 4:
        _head = _o[:_m.start()].strip()
        _k = max(1, int(round(han(_head) / max(1, han(_o)) * len(_sents(_t)))))
        _ts = _sents(_t)
        _htr = ''.join(_ts[:_k])
        HEADS[_p] = (_head, _htr)
        ZI[_p - 1] = [(_o[_m.start():].strip(), _t[len(_htr):])] + ZI[_p - 1][1:]""")

# B. 篇1 標題後插入鈔首
s = s.replace("""    if front:
        q = doc.add_paragraph(); q.paragraph_format.space_before = Pt(10)""",
"""    if p == 1:
        sp0 = [x.strip() for x in io.open(os.path.join(B, 'TXT_分卷', '01_行事鈔', '00_卷首.txt'), encoding='utf-8').read().split('\\n')[5:] if x.strip()]
        tp0 = os.path.join(B, 'AI語譯', 'out', '01_行事鈔', '00_卷首.txt')
        tt0 = [x.strip() for x in re.split(r'\\r?\\n\\r?\\n', io.open(tp0, encoding='utf-8').read()) if x.strip()]
        q = doc.add_paragraph(); q.paragraph_format.space_before = Pt(12)
        sr(q.add_run('〔鈔首〕序與十門'), 12, bold=True, color=RGBColor(0x6b, 0x5b, 0x4a))
        for i in range(min(len(sp0), len(tt0), 6)):
            qq = doc.add_paragraph(); qf = qq.paragraph_format
            qf.space_before = Pt(6); qf.space_after = Pt(1); qf.line_spacing = 1.2; qf.keep_with_next = True
            sr(qq.add_run('【鈔首%02d】' % (i + 1) + sp0[i]), 10, color=RGBColor(0x6b, 0x5b, 0x4a)); shade(qq, 'F4EFE2')
            a2 = doc.add_paragraph(); a2.paragraph_format.first_line_indent = Pt(20)
            a2.paragraph_format.line_spacing = 1.3; a2.paragraph_format.space_after = Pt(2)
            sr(a2.add_run(tt0[i]), 10.5)

    if front:
        q = doc.add_paragraph(); q.paragraph_format.space_before = Pt(10)""")

# C. 主程式結束後把頭部補到前一篇
s = s.replace("""        out, nc, nz, used = build(p, splits)
        print('篇%02d %-8s 鈔%3d 記%3d 切點%2d → %s' % (p, SECS[p - 1]['name'], nc, nz, len(splits), os.path.basename(out)))""",
"""        out, nc, nz, used = build(p, splits)
        print('篇%02d %-8s 鈔%3d 記%3d 切點%2d → %s' % (p, SECS[p - 1]['name'], nc, nz, len(splits), os.path.basename(out)))
    # 各篇首記的前篇尾巴 → 補到前一篇
    for p, (head, htr) in HEADS.items():
        fp = os.path.join(B, '白話', '會本_篇%02d_%s.docx' % (p - 1, SECS[p - 2]['name']))
        if not os.path.exists(fp):
            continue
        d = Document(fp)
        emit_ji_to(d, '【記%03d】（續前篇）' % len(ZI[p - 2]), head, htr)
        d.save(fp)
        print('  已補前篇尾巴到 篇%02d' % (p - 1))""")

# D. 獨立 emit 函式（供補尾巴用）
s = s.replace("""def build(p, splits):""",
"""def emit_ji_to(doc, tag, text, tr):
    r = doc.add_paragraph(); rf = r.paragraph_format
    rf.space_before = Pt(4); rf.space_after = Pt(1); rf.line_spacing = 1.2
    rf.left_indent = Pt(14); rf.keep_with_next = True
    sr(r.add_run(tag + text), 9.5, color=RGBColor(0x21, 0x5a, 0x8a)); shade(r, 'EEF2F6')
    b = doc.add_paragraph(); b.paragraph_format.first_line_indent = Pt(20)
    b.paragraph_format.left_indent = Pt(14)
    b.paragraph_format.line_spacing = 1.28; b.paragraph_format.space_after = Pt(2)
    sr(b.add_run(tr), 10)


def build(p, splits):""")
io.open(p, 'w', encoding='utf-8').write(s)
print('mk_pian_split patched: heads + 鈔首')
