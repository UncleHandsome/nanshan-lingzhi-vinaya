import glob
from docx import Document
from docx.shared import Pt, RGBColor
from docx.oxml.ns import qn

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\白話'
fp = glob.glob(B + r'\會本_篇01_*.docx')[0]
d = Document(fp)
ps = d.paragraphs

def idx_of(startswith):
    for i, p in enumerate(ps):
        if p.text.strip().startswith(startswith):
            return i
    return None

i51 = idx_of('【鈔首51】')
i185 = idx_of('【記185】')
print('idx', i51, i185)
if i51 is not None and i185 is not None and i51 < i185:
    tag = ps[i185].text
    body = ps[i185 + 1].text
    k = tag.find('第二門')
    kt = body.find('第二門')
    if k > 0 and kt > 0:
        tag1 = '【記185】（前半）' + tag[3:][:k - 3].strip()
        tag2 = '【記185】（後半）' + tag[3:][k - 3:].strip()
        body1 = body[:kt]
        body2 = body[kt:]
        # 建立新段落
        p_tag1 = d.add_paragraph(); r = p_tag1.add_run(tag1); r.font.size = Pt(9.5)
        p_body1 = d.add_paragraph(); r = p_body1.add_run(body1); r.font.size = Pt(10)
        p_tag2 = d.add_paragraph(); r = p_tag2.add_run(tag2); r.font.size = Pt(9.5)
        p_body2 = d.add_paragraph(); r = p_body2.add_run(body2); r.font.size = Pt(10)
        # 移到鈔首51 之前：記185前 + 鈔首51 + 記185後
        el51 = ps[i51]._element
        el51.addprevious(p_tag1._element)
        el51.addprevious(p_body1._element)
        # 記185 後半放到原記185 位置並刪除原記185
        old_tag, old_body = ps[i185]._element, ps[i185 + 1]._element
        old_tag.addprevious(p_tag2._element)
        old_tag.addprevious(p_body2._element)
        old_tag.getparent().remove(old_tag)
        old_body.getparent().remove(old_body)
        d.save(fp)
        print('鈔首51 已移到記185 前後半之間')
    else:
        print('找不到切點', k, kt)
