from docx import Document

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\白話'

def set_text(p, text):
    if p.runs:
        for r in p.runs[1:]:
            r.text = ''
        p.runs[0].text = text
    else:
        p.add_run(text)

f = B + r'\會本_篇18_四藥受淨.docx'
d = Document(f)
ps = d.paragraphs
idx = {}
for i, p in enumerate(ps):
    for k in ('【記098】（前）', '【記098】（中）', '【記098】（後）'):
        if p.text.strip().startswith(k):
            idx[k] = i
if len(idx) == 3:
    b1, b2, b3 = ps[idx['【記098】（前）'] + 1], ps[idx['【記098】（中）'] + 1], ps[idx['【記098】（後）'] + 1]
    tail = '這只是接受之後經過了一夜，並不是已經犯過戒的藥物。'
    paren = '（過去有人從自己或他人來區分差別，這是不對的。）'
    mid = '能授藥者的四種法則，大致與前面相同。'
    t3 = b3.text
    k = t3.find('在第三部分所列的五種過失中')
    set_text(b1, b1.text.rstrip() + tail + paren)
    set_text(b2, mid)
    set_text(b3, t3[k:] if k > 0 else t3)
    d.save(f)
    print('記098 已重排')
