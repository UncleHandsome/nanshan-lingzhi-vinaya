import glob, re
from docx import Document

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\白話'

def load(p):
    fp = glob.glob(B + r'\會本_篇%02d_*.docx' % p)[0]
    return Document(fp), fp

def set_text(p, text):
    if p.runs:
        for r in p.runs[1:]:
            r.text = ''
        p.runs[0].text = text
    else:
        p.add_run(text)

# 篇7
d, fp = load(7)
n = 0
for p in d.paragraphs:
    t = p.text
    t2 = t
    t2 = t2.replace('才稱為「非法羯磨」', '才稱為「如法羯磨」')
    t2 = t2.replace('在《僧祇論》中，一併說明了上座軌範', '在《摩得伽論》中，一併說明了上座軌範')
    t2 = re.sub(r'佛在舍\s*[，,]\s*\S{0,3}?\s*因智慧', '佛在舍衛國，因智慧', t2)
    t2 = t2.replace('絆即 束', '絆即拘束').replace('絆即束', '絆即拘束')
    if t2 != t:
        set_text(p, t2)
        n += 1
d.save(fp)
print('篇7 文字修正', n, '處')

# 篇1 記450 尾 "2"
d, fp = load(1)
for i, p in enumerate(d.paragraphs):
    if p.text.strip().startswith('【記450】'):
        t = p.text
        if t.rstrip().endswith('2'):
            set_text(p, t.rstrip()[:-1].rstrip())
            d.save(fp)
            print('篇1 記450 尾 2 已刪')
        break
