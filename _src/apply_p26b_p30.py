import io, os, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
T26 = io.open(os.path.join(B, '_src', 't_p26.txt'), encoding='utf-8').read().strip()
fp = os.path.join(B, 'AI語譯', 'out', '01_行事鈔', '12a_卷下之四.txt')
tt = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(fp, encoding='utf-8').read()) if x.strip()]
n = 0
for i, t in enumerate(tt):
    k = t.find('若法師者云')
    if k > 0:
        tt[i] = t[:k] + T26
        n += 1
io.open(fp, 'w', encoding='utf-8').write('\n\n'.join(tt) + '\n')
print('篇26 已改', n, '段')

# 篇30 後跋：以編者按插入 docx（在記026 之前）
from docx import Document
from docx.shared import Pt, RGBColor
f30 = os.path.join(B, '白話', '會本_篇30_諸部別行.docx')
d = Document(f30)
ps = d.paragraphs
for i, p in enumerate(ps):
    if p.text.strip().startswith('【記026】'):
        q = d.add_paragraph()
        r = q.add_run('【編者按】道宣律師後跋原文（T40n1804_p0156c27–30）：「余於唐武德九年六月內，爾時搜揚僧伍，無傷俗譽，且閉戶依所學撰次。但意在行用，直筆書通，不事虬文，故言多蹇陋。想有識通士，知余記志焉。」')
        r.font.size = Pt(9)
        r.font.color.rgb = RGBColor(0x88, 0x55, 0x22)
        p._element.addprevious(q._element)
        d.save(f30)
        print('篇30 後跋按語已插入')
        break
