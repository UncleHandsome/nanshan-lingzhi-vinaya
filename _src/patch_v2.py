
import io
p = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\_src\build_baihua.py'
s = io.open(p, encoding='utf-8').read()

# 1) trans path -> trans2
s = s.replace("os.path.join(SRC, 'trans', fn)", "os.path.join(SRC, 'trans2', fn)")

# 2) cover subtitle
old = "    set_run(p.add_run('白話語譯' + ('‧對照本' if mode == 'dui' else '‧全白話本')), 15)"
new = "    set_run(p.add_run('白話語譯' + ('‧對照本' if mode == 'dui' else '‧全白話本') + '（修訂版）'), 15)"
assert s.count(old) == 1
s = s.replace(old, new)

# 3) notes loader + renderer, inserted before def build(
helper = '''
def load_notes(fn):
    d = {}
    cur = None; buf = []
    for line in io.open(os.path.join(SRC, 'trans2', fn), encoding='utf-8').read().split('\\n'):
        m = re.match(r'^@(\\d+)\\.(\\d+)\\s*$', line.strip())
        if m:
            if cur: d[cur] = '\\n'.join(buf).strip()
            cur = m.group(1) + '.' + m.group(2); buf = []
        else:
            buf.append(line)
    if cur: d[cur] = '\\n'.join(buf).strip()
    return d

NOTES = load_notes('notes.txt')

def add_note(doc, text):
    for i, line in enumerate([x for x in text.split('\\n') if x.strip()]):
        q = doc.add_paragraph()
        q.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        qf = q.paragraph_format
        qf.left_indent = Pt(24); qf.first_line_indent = Pt(0)
        qf.line_spacing = 1.25; qf.space_before = Pt(1); qf.space_after = Pt(3)
        set_run(q.add_run('註　' if i == 0 else '　　'), 9, bold=True, color=RGBColor(0x8a, 0x6d, 0x3b))
        set_run(q.add_run(line), 9, color=RGBColor(0x5f, 0x5f, 0x5f))

def build('''
assert s.count('\ndef build(') == 1
s = s.replace('\ndef build(', helper, 1)

# 4) note call after translation run
old4 = "                set_run(p.add_run(tr), 12 if mode == 'qian' else 11.5)"
new4 = ("                set_run(p.add_run(tr), 12 if mode == 'qian' else 11.5)\n"
        "                nt = NOTES.get('%d.%d' % (si, idx))\n"
        "                if nt:\n"
        "                    add_note(doc, nt)")
assert s.count(old4) == 1
s = s.replace(old4, new4)

# 5) revision appendix before doc.save
old5 = "    doc.save(out_docx)"
new5 = '''    # 修訂說明
    p = doc.add_paragraph()
    p.paragraph_format.page_break_before = True
    p.paragraph_format.space_after = Pt(10)
    set_run(p.add_run('修訂說明'), 16, bold=True)
    p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(8)
    set_run(p.add_run('本版據《資持記》及律典重校，改正前版錯譯與「照抄式」譯文，要點如下：'), 10, color=RGBColor(0x66, 0x66, 0x66))
    fixes = [
        ('震嶺', '前譯作「鷲嶺」，誤。今改「漢地（震旦）」；九代指後漢至唐九朝。'),
        ('易以形聲', '前譯作「落實在形聲上就難」，義反。今改「容易藉言語音聲做表面文章」。'),
        ('眾網維持', '前譯成「要維持、要區別」，語氣反。今改「綱紀的維持、同異的分判都亂了套」。'),
        ('名僧', '前誤讀為「有名的僧人」。今改「以能秉法稱之為僧」。'),
        ('不敬上座無威儀', '前誤連讀成「不敬沒有威儀的上座」。今析為二事。'),
        ('五種怖畏', '前孤立列出「畜沙彌、與他依止」。今補明是無德而收徒。'),
        ('事在廢前', '前未譯。今加註：後代教法廢前代開緣。'),
        ('誼靜二儀', '前照抄。今改「喧靜二儀」並註明疑為形訛。'),
        ('五大色', '前照抄。今補明五正色與壞色之制。'),
        ('停僧殘行法', '前語意混亂。今補明開許充數及「和尚犯戒、戒子不知情」之義。'),
        ('度量衡', '前僅照錄步數。今補一步六尺、一肘尺八、七樹六十三步之理。'),
        ('偽白話', '前有多段僅換虛詞、甚至照抄（如「宅身佛海」「測思明慧」等），今全部改寫為現代漢語。'),
    ]
    for k, v in fixes:
        q = doc.add_paragraph(); q.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        qf = q.paragraph_format; qf.first_line_indent = Pt(20); qf.line_spacing = 1.35; qf.space_after = Pt(3)
        set_run(q.add_run(k + '：'), 9.5, bold=True)
        set_run(q.add_run(v), 9.5)
    doc.save(out_docx)'''
assert s.count(old5) == 1
s = s.replace(old5, new5)

# 6) output names
s = s.replace("行事鈔_白話對照本_卷一.docx", "行事鈔_白話對照本_卷一_修訂版.docx")
s = s.replace("行事鈔_全白話本_卷一.docx", "行事鈔_全白話本_卷一_修訂版.docx")

io.open(p, 'w', encoding='utf-8').write(s)
print('patched')
