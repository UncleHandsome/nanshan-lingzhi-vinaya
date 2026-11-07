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

# A. 篇29 記002 中 → 前
d, fp = load(29); ps = d.paragraphs
i2p = find(ps, '【記002】（前）'); i2m = find(ps, '【記002】（中）')
if None not in (i2p, i2m):
    bm = ps[i2m + 1]; bp = ps[i2p + 1]
    tail = '接著引用論典來做解釋，文中所說的「不便」，是指若將男女法位直接互相配對，容易招致世人的譏嫌與猜疑。'
    if tail in bm.text:
        set_text(bp, bp.text.rstrip() + tail)
        set_text(bm, bm.text.replace(tail, '', 1).lstrip())
        d.save(fp); print('篇29 記002 譯文回前')

# B. 篇1 記450 尾 篇2 殘文
d, fp = load(1); ps = d.paragraphs
i = find(ps, '【記450】')
if i is not None:
    b = ps[i + 1]; t = b.text
    k = t.find('解釋集僧篇')
    if k > 0:
        set_text(b, t[:k].rstrip())
        d.save(fp); print('篇1 記450 尾清除')

# E. 篇27 記041 三段歸 鈔40/41/42
d, fp = load(27); ps = d.paragraphs
tags = [p.text.strip() for p in ps if p.text.strip().startswith('【記041】')]
print('篇27 記041 片數', len(tags))

# H. 篇7 記007 前半尾句 → 後半頭
d, fp = load(7); ps = d.paragraphs
ip = find(ps, '【記007】（前半）'); ih = find(ps, '【記007】（後半）')
if None not in (ip, ih):
    bp, bh = ps[ip + 1], ps[ih + 1]
    sent = '化教法門的標題中，通指道俗二眾，略微展示化導之義；'
    if sent in bp.text and sent not in bh.text:
        set_text(bp, bp.text.replace(sent, '').rstrip())
        set_text(bh, sent + bh.text)
        d.save(fp); print('篇7 記007 譯文回後半')

# I. 篇7 記017 後半大段 → 前半
d, fp = load(7); ps = d.paragraphs
ip = find(ps, '【記017】（前半）'); ih = find(ps, '【記017】（後半）')
if None not in (ip, ih):
    bp, bh = ps[ip + 1], ps[ih + 1]
    t = bh.text
    k = t.find('《涅槃》中')
    if k > 0:
        set_text(bp, bp.text.rstrip() + t[:k])
        set_text(bh, t[k:])
        d.save(fp); print('篇7 記017 譯文回前半')
