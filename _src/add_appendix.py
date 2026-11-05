
import io
p = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\_src\build_vol.py'
s = io.open(p, encoding='utf-8').read()
old = "    doc.save(path)\n    return len(doc.paragraphs)"
new = """    if vol == '下卷':
        p = doc.add_paragraph(); p.paragraph_format.page_break_before = True
        p.paragraph_format.space_after = Pt(8)
        set_run(p.add_run('附錄一　律典簡稱對照'), 15, bold=True)
        rows1 = [('《四分》', '《四分律》'), ('《僧祇》', '《摩訶僧祇律》'), ('《十誦》', '《十誦律》'),
                 ('《五分》', '《彌沙塞部和醯五分律》'), ('《善見》', '《善見律毘婆沙》'),
                 ('《多論》／《薩婆多》', '《薩婆多毘尼毘婆沙》'), ('《伽論》', '《薩婆多部毘尼摩得勒伽》'),
                 ('《母論》', '《毘尼母經》'), ('《明了》', '《律二十二明了論》'),
                 ('《義鈔》', '道宣《四分律拾毗尼義鈔》'), ('《大疏》', '首師《四分律疏》二十卷'),
                 ('《資持記》', '元照《四分律行事鈔資持記》')]
        for a, b in rows1:
            q = doc.add_paragraph(); qf = q.paragraph_format
            qf.left_indent = Pt(12); qf.space_after = Pt(1); qf.line_spacing = 1.25
            set_run(q.add_run(a), 9.5, bold=True); set_run(q.add_run('　＝　'), 9.5); set_run(q.add_run(b), 9.5)
        p = doc.add_paragraph(); p.paragraph_format.space_before = Pt(14); p.paragraph_format.space_after = Pt(8)
        set_run(p.add_run('附錄二　律度量衡與今制約算'), 15, bold=True)
        rows2 = [('一肘', '一尺八寸，約 45 公分'), ('一搩手', '中指至拇指張開，約 20–25 公分'),
                 ('一弓', '五肘，約 2.2 公尺'), ('一步', '六尺，約 1.4–1.8 公尺（本文以一步六尺計）'),
                 ('一拘盧舍', '五百弓／六百步，約 0.8–1 公里（《雜寶藏》作五里）'),
                 ('一由旬', '約 7–15 公里（小由旬約 40 里）'), ('一槃陀', '二十八肘，約 12.6 公尺'),
                 ('一斛', '十斗，約 60 公升（唐制）'), ('一秤', '約 1.5 公斤（本文「三十秤」約 45 公斤）')]
        for a, b in rows2:
            q = doc.add_paragraph(); qf = q.paragraph_format
            qf.left_indent = Pt(12); qf.space_after = Pt(1); qf.line_spacing = 1.25
            set_run(q.add_run(a), 9.5, bold=True); set_run(q.add_run('　'), 9.5); set_run(q.add_run(b), 9.5)
        q = doc.add_paragraph(); q.paragraph_format.space_before = Pt(8)
        set_run(q.add_run('（以上折算依唐制與諸律互參，僅供閱讀參考；實際結界、裁衣仍應依師承與律本。）'), 8.5, color=RGBColor(0x77, 0x77, 0x77))
    doc.save(path)
    return len(doc.paragraphs)"""
assert s.count(old) == 1
s = s.replace(old, new)
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
