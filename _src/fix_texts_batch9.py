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

fixes = {
    5: [('余親問中國三藏京輦翻經諸師，云：從佛滅度來，無有此法。',
         '我曾親自詢問京城中翻譯經典的三藏諸師，他們都說：自從佛陀滅度以來，從未有過這種做法。'),
        ('5 『釋羯磨篇（上篇之一的下半部）』『釋羯磨篇』：', '')],
    7: [('7 釋僧網篇（上之二）解釋〈僧網篇〉：', '')],
    8: [('《四分律行事鈔資持記》卷上三之八，解釋〈受戒篇〉：', '')],
}
for p, subs in fixes.items():
    d, fp = load(p)
    n = 0
    for par in d.paragraphs:
        t = par.text
        t2 = t
        for a, b in subs:
            if a in t2:
                t2 = t2.replace(a, b)
        if t2 != t:
            set_text(par, t2.lstrip())
            n += 1
    d.save(fp)
    print('篇%d 修正 %d 段' % (p, n))

# 篇8 記028（後半）標籤多餘括號
d, fp = load(8)
for par in d.paragraphs:
    if par.text.strip().startswith('【記028】（後半）請和尚中。）'):
        set_text(par, par.text.rstrip()[:-1].rstrip())
        d.save(fp)
        print('篇8 記028 括號已清')
        break
