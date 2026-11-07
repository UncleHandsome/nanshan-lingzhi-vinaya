import glob
from docx import Document

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\白話'
for p, key in [(21, '【記062】'), (22, '【記001】'), (23, '【記058】'), (24, '【記001】'),
               (27, '【記048】'), (28, '【記001】'), (29, '【記055】'), (30, '【記001】')]:
    f = glob.glob(B + r'\會本_篇%02d_*.docx' % p)[0]
    ps = [x.text.strip() for x in Document(f).paragraphs]
    print('=== 篇', p)
    for i, t in enumerate(ps):
        if t.startswith(key):
            print(' tag:', t[:30])
            print(' 譯:', ps[i + 1][:50])
            break
    print(' 末2:', [x[:34] for x in ps[-2:]])
