import io, os, re
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

# ---------- 篇18 記098 ----------
f = os.path.join(WH, '會本_篇18_四藥受淨.docx')
d = Document(f)
ps = [p for p in d.paragraphs]
idx = {}
for i, p in enumerate(ps):
    t = p.text.strip()
    for k in ('【記098】（前）', '【記098】（中）', '【記098】（後）'):
        if t.startswith(k):
            idx[k] = i
if len(idx) == 3:
    b前, b中, b後 = ps[idx['【記098】（前）'] + 1], ps[idx['【記098】（中）'] + 1], ps[idx['【記098】（後）'] + 1]
    tail = '這只是接受之後經過了一夜，並不是已經犯過戒的藥物。'
    paren = '（過去有人從自己或他人來區分差別，這是不對的。）'
    mid = '能授藥者的四種法則，大致與前面相同。'
    t後 = b後.text
    k = t後.find('在第三部分所列的五種過失中')
    rest = t後[k:] if k > 0 else t後
    set_text(b前, b前.text.rstrip() + tail + paren)
    set_text(b中, mid)
    set_text(b後, rest)
    d.save(f)
    print('篇18 記098 已重排')

# ---------- 篇14 記043/044 ----------
f = os.path.join(WH, '會本_篇14_隨戒釋相.docx')
d = Document(f)
ps = [p for p in d.paragraphs]
i43 = i44 = None
for i, p in enumerate(ps):
    if p.text.strip().startswith('【記043】'):
        i43 = i
    if p.text.strip().startswith('【記044】'):
        i44 = i
if i43 is not None and i44 is not None:
    b43, b44 = ps[i43 + 1], ps[i44 + 1]
    t = b43.text
    k = t.find('戒淨障業')
    if k > 0:
        moved = t[k:]
        set_text(b43, t[:k].rstrip())
        set_text(b44, moved.rstrip() + b44.text)
        d.save(f)
        print('篇14 記043→044 譯文已移回')
    else:
        print('篇14 找不到 戒淨障業')
