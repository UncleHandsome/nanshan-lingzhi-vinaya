import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\mk_pian_split.py'
s = io.open(p, encoding='utf-8').read()

# 篇4：把「四俱是，可知。」從記50 移到記49 末
s = s.replace("""def strip_dup_tail(p):""",
"""def move_siju():
    o49, t49 = ZI[3][48]
    o50, t50 = ZI[3][49]
    key = '四俱是，可知。'
    if o50.startswith(key):
        ZI[3][48] = (o49 + key, t49)
        ZI[3][49] = (o50[len(key):], t50)


def strip_dup_tail(p):""")
s = s.replace("""        strip_dup_tail(p)""", """        move_siju()
        strip_dup_tail(p)""")

# 篇1：鈔首後補十門
s = s.replace("""    if front:
        q = doc.add_paragraph(); q.paragraph_format.space_before = Pt(10)""",
"""    if p == 1:
        MEN = [
            '第一門：序教興意', '第二門：教網綱要意', '第三門：對事約教制處意',
            '第四門：用諸部文意', '第五門：文義決通意', '第六門：教所詮意',
            '第七門：道俗七部立教通局意', '第八門：僧尼二部行事通塞意',
            '第九門：下三眾隨行異同意', '第十門：引用正文去濫傳真科酌意',
        ]
        q = doc.add_paragraph(); q.paragraph_format.space_before = Pt(8)
        sr(q.add_run('【鈔首・十門】'), 11, bold=True, color=RGBColor(0x6b, 0x5b, 0x4a))
        intro = ('然一部之文，義張三位：上卷則攝於眾務，成用有儀；中卷則遵於戒體，持犯立懺；'
                 '下卷則隨機要行，託事而起。今取物類相從者，以標名首；更以十門例括：')
        q2 = doc.add_paragraph(); q2.paragraph_format.first_line_indent = Pt(20)
        q2.paragraph_format.line_spacing = 1.3; q2.paragraph_format.space_after = Pt(2)
        sr(q2.add_run(intro), 10.5)
        for i, m in enumerate(MEN):
            qm = doc.add_paragraph(); qm.paragraph_format.left_indent = Pt(16)
            qm.paragraph_format.space_before = Pt(1); qm.paragraph_format.space_after = Pt(1)
            sr(qm.add_run(m), 10.5)

    if front:
        q = doc.add_paragraph(); q.paragraph_format.space_before = Pt(10)""")
io.open(p, 'w', encoding='utf-8').write(s)
print('siju move + 十門 added')
