import glob, io, os, re
from docx import Document

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
WH = os.path.join(B, '白話')

def set_text(p, text):
    if p.runs:
        for r in p.runs[1:]:
            r.text = ''
        p.runs[0].text = text
    else:
        p.add_run(text)

def load(p):
    return Document(glob.glob(WH + r'\會本_篇%02d_*.docx' % p)[0])

def save(d, p):
    d.save(glob.glob(WH + r'\會本_篇%02d_*.docx' % p)[0])

def find(ps, key):
    for i, x in enumerate(ps):
        if x.text.strip().startswith(key):
            return i
    return None

# ---- 篇23 鈔04 一句補譯 ----
d = load(23); ps = d.paragraphs
i = find(ps, '【鈔04】')
if i is not None:
    b = ps[i + 1]
    old = '若施主未知請僧法，知識尼得教安置形像，益食法已，然後坐；應在別處，又不得勝僧所。'
    new = ('如果施主不懂得請僧應供的法度，熟識的善知識比丘尼可以從旁指導如何安奉佛像與盛飯添食之法，交代完畢後方可入座；'
           '比丘尼的席位應當安置在另外的偏處，而且絕對不可以優於比丘僧的席位。')
    if old in b.text:
        set_text(b, b.text.replace(old, new))
        save(d, 23); print('篇23 鈔04 補譯 ok')

# ---- 篇12 記080/081 括號 ----
d = load(12); ps = d.paragraphs
i80 = find(ps, '【記080】'); i81 = find(ps, '【記081】')
if i80 is not None and i81 is not None:
    t81 = ps[i81].text
    if t81.replace('【記081】', '').startswith('〕'):
        ps[i81].runs[0].text = '【記081】' + t81.replace('【記081】', '').lstrip('〕').lstrip()
        b80 = ps[i80 + 1]
        set_text(b80, b80.text.rstrip() + '〕')
        save(d, 12); print('篇12 括號 ok')

# ---- 篇10 記049 跨頁句移回 ----
d = load(10); ps = d.paragraphs
i = find(ps, '【記049】（前半）'); j = find(ps, '【記049】（後半）')
if i is not None and j is not None:
    tail = '「唱法」、「打靜」中，指〈雜行篇〉。'
    b1, b2 = ps[i + 1], ps[j + 1]
    if tail in b1.text and tail not in b2.text:
        set_text(b1, b1.text.replace(tail, '').rstrip())
        set_text(b2, tail + b2.text)
        save(d, 10); print('篇10 記049 ok')

# ---- 篇3 記056 譯文回前半 ----
d = load(3); ps = d.paragraphs
i = find(ps, '【記056】（前半）'); j = find(ps, '【記056】（後半）')
if i is not None and j is not None:
    b1, b2 = ps[i + 1], ps[j + 1]
    t2 = b2.text
    cut = t2.find('律中凡從僧乞法')
    if cut > 0:
        set_text(b1, b1.text.rstrip() + t2[:cut])
        set_text(b2, t2[cut:])
        save(d, 3); print('篇3 記056 ok')
