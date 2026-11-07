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

# ---- 篇8 記042 譯文回前半 ----
f8 = glob.glob(WH + r'\會本_篇08_*.docx')[0]
d = Document(f8); ps = d.paragraphs
i = j = None
for k, p in enumerate(ps):
    if p.text.strip().startswith('【記042】（前半）'):
        i = k
    if p.text.strip().startswith('【記042】（後半）'):
        j = k
print('篇8 idx', i, j)
if i is not None and j is not None:
    b1, b2 = ps[i + 1], ps[j + 1]
    t2 = b2.text
    cut = t2.find('在通泛簡選')
    if cut > 0:
        moved = t2[:cut]
        set_text(b1, b1.text.rstrip() + moved)
        set_text(b2, t2[cut:])
        d.save(f8)
        print('篇8 記042 已移回，長度', len(moved))

# ---- 篇26 譯文位移偵測 ----
han = lambda s: ''.join(re.findall(r'[\u4e00-\u9fff]', s))
def grams(s, n=2):
    h = han(s)
    return {h[i:i + n] for i in range(len(h) - n + 1)}
for f in glob.glob(os.path.join(B, 'TXT_分卷', '01_行事鈔', '*.txt')):
    k = os.path.basename(f)[:-4]
    sp = [x.strip() for x in io.open(f, encoding='utf-8').read().split('\n')[5:] if x.strip()]
    if not any('二明送終法' in x or '當從像前' in x for x in sp):
        continue
    tp = os.path.join(B, 'AI語譯', 'out', '01_行事鈔', k + '.txt')
    tt = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(tp, encoding='utf-8').read()) if x.strip()]
    best, bk = -1, 0
    for sh in range(-3, 4):
        tot = 0
        for i2 in range(len(sp)):
            j2 = i2 + sh
            if 0 <= j2 < len(tt):
                tot += len(grams(sp[i2]) & grams(tt[j2]))
        if tot > best:
            best, bk = tot, sh
    print(k, 'shift', bk, 'score', best, 'len', len(sp), len(tt))
