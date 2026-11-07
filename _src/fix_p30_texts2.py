import glob
from docx import Document

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\白話'
fp = glob.glob(B + r'\會本_篇30_*.docx')[0]
d = Document(fp)
ps = d.paragraphs

def find(key):
    for i, x in enumerate(ps):
        if x.text.strip().startswith(key):
            return i
    return None

def set_text(p, text):
    if p.runs:
        for r in p.runs[1:]:
            r.text = ''
        p.runs[0].text = text
    else:
        p.add_run(text)

def move(src, dst, needle):
    a, b = find(src), find(dst)
    if a is None or b is None:
        print('缺', src, dst); return
    s, t = ps[a + 1], ps[b + 1]
    k = s.text.find(needle)
    if k < 0:
        print('缺句', needle); return
    set_text(s, s.text[:k].rstrip())
    set_text(t, t.text.rstrip() + s.text if False else t.text.rstrip() + s.text[k:] if False else t.text.rstrip())

# 重寫：先取 moved
def move2(src, dst, needle):
    a, b = find(src), find(dst)
    if a is None or b is None:
        print('缺', src, dst); return
    s, t = ps[a + 1], ps[b + 1]
    k = s.text.find(needle)
    if k < 0:
        print('缺句', needle); return
    moved = s.text[k:]
    set_text(s, s.text[:k].rstrip())
    set_text(t, t.text.rstrip() + moved)

i = find('【記001】')
if i is not None:
    tag, body = ps[i].text, ps[i + 1].text
    k, kt = tag.find('題標諸部'), body.find('第三十門')
    if k > 0:
        set_text(ps[i], '【記001】' + tag[k:])
    if kt > 0:
        set_text(ps[i + 1], body[kt:])

move2('【記011】（中）', '【記011】（前）', '暫且列舉五處')
move2('【記016】（中）', '【記016】（前）', '學悔期間違犯僧殘')
move2('【記016】（後）', '【記016】（中）', '古代天竺在夏季')

i1, i2, i3 = find('【記019】（一）'), find('【記019】（二）'), find('【記019】（三）')
if None not in (i1, i2, i3):
    b1, b2, b3 = ps[i1 + 1], ps[i2 + 1], ps[i3 + 1]
    s1 = '《僧祇律》中將遮戒與性戒分成兩類處理。'
    s3 = '《十誦律》則區分有無犯戒的前方便。'
    if s1 in b1.text:
        set_text(b1, b1.text.replace(s1, '').rstrip())
    set_text(b2, s1)
    set_text(b3, s3 + b3.text)

d.save(fp)
print('篇30 修正完成')
