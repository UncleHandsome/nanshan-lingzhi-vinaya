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

# 篇8：記042（後半）整段併入記043 開頭
d, fp = load(8); ps = d.paragraphs
i42b = find(ps, '【記042】（後半）'); i43 = find(ps, '【記043】')
if i42b is not None and i43 is not None:
    t42 = ps[i42b].text.replace('【記042】（後半）', '').strip()
    b42 = ps[i42b + 1]
    t43 = ps[i43].text.replace('【記043】', '').lstrip('\U000F0EA2󰺢').lstrip('臘')
    set_text(ps[i43], '【記043】' + t42 + t43)
    set_text(ps[i43 + 1], b42.text + ps[i43 + 1].text)
    for el in (ps[i42b]._element, b42._element):
        el.getparent().remove(el)
    d.save(fp)
    print('篇8 記042後半併入043')

# 篇1：記449 前半併回記448
d, fp = load(1); ps = d.paragraphs
i448 = find(ps, '【記448】'); i449 = find(ps, '【記449】')
if i448 is not None and i449 is not None:
    t = ps[i449].text.replace('【記449】', '')
    k = t.find('好作下')
    if k > 0:
        set_text(ps[i448], ps[i448].text.rstrip() + t[:k].rstrip())
        set_text(ps[i449], '【記449】' + t[k:])
        d.save(fp)
        print('篇1 記449 前半併回448')

# 篇30：記001 前半移到篇29 末記
d30, fp30 = load(30); ps30 = d30.paragraphs
i1 = find(ps30, '【記001】')
if i1 is not None:
    t = ps30[i1].text.replace('【記001】', '')
    k = t.find('30 釋諸部篇')
    if k > 0:
        prefix = t[:k].rstrip()
        set_text(ps30[i1], '【記001】' + t[k:])
        d30.save(fp30)
        d29, fp29 = load(29); ps29 = d29.paragraphs
        idx = max(i for i, p in enumerate(ps29) if p.text.strip().startswith('【記'))
        set_text(ps29[idx], ps29[idx].text.rstrip() + prefix)
        d29.save(fp29)
        print('篇30 記001 前半移回篇29')
