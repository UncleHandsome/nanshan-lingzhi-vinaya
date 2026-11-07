import glob
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

d30, fp30 = load(30); ps = d30.paragraphs
i = find(ps, '【記001】')
if i is not None:
    tag = ps[i].text
    body = ps[i + 1].text
    k = tag.find('題標諸部')
    kt = body.find('第三十門')
    if k > 0:
        pre_tag = tag[:k].replace('【記001】', '').rstrip()
        pre_tr = body[:kt].rstrip() if kt > 0 else ''
        set_text(ps[i], '【記001】' + tag[k:])
        set_text(ps[i + 1], body[kt:] if kt > 0 else body)
        d30.save(fp30)
        d29, fp29 = load(29); ps29 = d29.paragraphs
        idx = max(j for j, p in enumerate(ps29) if p.text.strip().startswith('【記'))
        set_text(ps29[idx], ps29[idx].text.rstrip() + pre_tag)
        set_text(ps29[idx + 1], ps29[idx + 1].text.rstrip() + pre_tr)
        d29.save(fp29)
        print('篇30 記001 前半已移回篇29')
