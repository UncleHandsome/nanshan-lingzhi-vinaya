import glob, re
from docx import Document

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\白話'

def load(p):
    return Document(glob.glob(B + r'\會本_篇%02d_*.docx' % p)[0]), glob.glob(B + r'\會本_篇%02d_*.docx' % p)[0]

def find(ps, key):
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

# 1) 篇8 記039 木叉
d, fp = load(8); ps = d.paragraphs
i38, i39 = find(ps, '【記038】'), find(ps, '【記039】')
if i38 is not None and i39 is not None:
    t39 = ps[i39].text
    if '叉' in t39[:8]:
        k = t39.find('】') + 1
        body = t39[k:]
        if body.startswith('叉'):
            set_text(ps[i38], ps[i38].text.rstrip() + '叉')
            set_text(ps[i39], '【記039】' + body[1:])
            d.save(fp); print('篇8 記039 木叉 ok')

# 2) 篇8 記042 通簡中 → 記043
d, fp = load(8); ps = d.paragraphs
i42 = find(ps, '【記042】'); i43 = find(ps, '【記043】')
if i42 is not None and i43 is not None:
    b = ps[i42 + 1]
    t = b.text
    k = t.find('通簡中')
    if k > 0:
        moved = t[k:]
        set_text(b, t[:k].rstrip())
        set_text(ps[i43 + 1], moved + ps[i43 + 1].text)
        d.save(fp); print('篇8 記042 通簡中移入043')

# 3) 篇8 記043 補臘
d, fp = load(8); ps = d.paragraphs
i = find(ps, '【記043】')
if i is not None:
    t = ps[i].text.replace('高德重', '臘高德重').replace('意取高', '意取高臘')
    set_text(ps[i], t)
    d.save(fp); print('篇8 記043 補字')

# 6) 篇3 記024 前半移到記023 後半之後
d, fp = load(3); ps = d.paragraphs
i23 = find(ps, '【記023】（前半）'); i23b = find(ps, '【記023】（後半）')
i24 = find(ps, '【記024】（前半）')
if None not in (i23, i23b, i24) and i24 < i23b:
    blk = [ps[i24]._element, ps[i24 + 1]._element]
    anchor = ps[i23b + 1]._element
    for el in blk:
        anchor.addnext(el)
    d.save(fp); print('篇3 記024 前半已後移')

# 7) 篇21 記062 尾標題
d, fp = load(21); ps = d.paragraphs
i = find(ps, '【記062】')
if i is not None:
    t = ps[i].text
    t2 = re.sub(r'22\s*釋僧像篇.*$', '', t).rstrip()
    if t2 != t:
        set_text(ps[i], t2)
        d.save(fp); print('篇21 記062 標題清除')

# 8) 篇10 記049 缺字
d, fp = load(10); ps = d.paragraphs
for p in ps:
    if '口𠻳' in p.text:
        set_text(p, p.text.replace('口𠻳', '漱口'))
        d.save(fp); print('篇10 補字 ok'); break
