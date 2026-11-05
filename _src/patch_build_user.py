
import io
p = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\_src\build_user.py'
s = io.open(p, encoding='utf-8').read()
old = "    doc.save(out_docx)"
new = '''    # 校改表
    p = doc.add_paragraph()
    p.paragraph_format.page_break_before = True
    p.paragraph_format.space_after = Pt(8)
    set_run(p.add_run('校改表'), 15, bold=True)
    p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(8)
    set_run(p.add_run('本版就已指出的錯譯逐條改正，並核以《資持記》及原書文例：'), 9.5, color=RGBColor(0x66, 0x66, 0x66))
    fixes = [
        ('震嶺', '前作「鷲嶺」。今改「震嶺（震旦）」，指漢地，非印度靈鷲山；九代指漢至唐九朝。'),
        ('斥其文繁', '前譯成「我斥責異說文繁」，主客顛倒。今改：異見者嫌我這部鈔文繁。'),
        ('眾網維持', '前譯成正面目標。今改：僧團綱紀的維持、同異的分判都亂了準則。'),
        ('起情虛實', '前作「起心動念之虛實」。今補明：疑心為虛、決定心為實。'),
        ('有義無文、無文有事', '前作「有理無文、有文無理」。今依《資持記》改正：有義而無明文；無明文而實有其事。'),
        ('墨印', '前作「法印」。今改「墨印」，並註明《資持記》以之即《四分》四說、以聖教印定。'),
        ('垂泥曰', '前作「垂死涅槃」。今改「即將入滅（垂泥曰）」。'),
        ('第十五卷', '前作「下卷第十五卷」。今改指道宣《四分律含注戒本疏》（大疏）卷十五。'),
        ('不敬上座無威儀', '前合為一句。今析為「不敬上座」與「自身無威儀」二事。'),
        ('身一面', '前作「身心任一面」。今改「身的一面」。'),
        ('合角量', '前作「折算拉平」。今改「合角量取」，即量其對角，最多三由旬。'),
    ]
    for k, v in fixes:
        q = doc.add_paragraph(); q.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        qf = q.paragraph_format; qf.first_line_indent = Pt(20); qf.line_spacing = 1.35; qf.space_after = Pt(3)
        set_run(q.add_run(k + '：'), 9.5, bold=True)
        set_run(q.add_run(v), 9.5)
    doc.save(out_docx)'''
assert s.count(old) == 1
s = s.replace(old, new)
s = s.replace("行事鈔_白話對照本_卷一_定本.docx", "行事鈔_白話對照本_卷一_定本v2.docx")
s = s.replace("行事鈔_全白話本_卷一_定本.docx", "行事鈔_全白話本_卷一_定本v2.docx")
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
