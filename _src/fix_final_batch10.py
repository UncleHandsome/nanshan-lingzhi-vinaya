import glob, re
from docx import Document

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\白話'

def load(p):
    fp = glob.glob(B + r'\會本_篇%02d_*.docx' % p)[0]
    return Document(fp), fp

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

# 篇7 記017 譯文回前半
d, fp = load(7); ps = d.paragraphs
ia, ib = find(ps, '【記017】（前半）'), find(ps, '【記017】（後半）')
if None not in (ia, ib):
    ba, bb = ps[ia + 1], ps[ib + 1]
    t = bb.text
    k = t.find('在《涅槃經》')
    if k > 0:
        set_text(ba, ba.text.rstrip() + t[:k])
        set_text(bb, t[k:])
        d.save(fp); print('篇7 記017 譯文回前半')

# 篇23 末尾殘標題
d, fp = load(23); ps = d.paragraphs
idx = max(i for i, p in enumerate(ps) if p.text.strip().startswith('【記'))
for j in (idx, idx + 1):
    if j < len(ps):
        t = ps[j].text
        t2 = re.sub(r'24\s*釋導俗篇.*$', '', t).rstrip()
        if t2 != t:
            set_text(ps[j], t2)
            print('篇23 殘標題清除', j)
d.save(fp)

# 篇1 末尾孤立 2
d, fp = load(1); ps = d.paragraphs
for i, p in enumerate(ps):
    if p.text.strip() == '2':
        p._element.getparent().remove(p._element)
        d.save(fp); print('篇1 孤立段 2 已刪')
        break
else:
    last = ps[-1]
    t = last.text.rstrip()
    if t.endswith('2'):
        set_text(last, t[:-1].rstrip())
        d.save(fp); print('篇1 末段尾 2 已刪')
