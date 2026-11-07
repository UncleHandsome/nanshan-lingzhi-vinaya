import glob
from docx import Document

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\白話'
checks = [(12, '【記001】'), (13, '【記135】'), (19, '【記040】'), (21, '【記062】'),
          (22, '【記080】'), (23, '【記058】'), (26, '【記005】'), (27, '【記048】')]
for p, key in checks:
    f = glob.glob(B + r'\會本_篇%02d_*.docx' % p)[0]
    ps = [x.text.strip() for x in Document(f).paragraphs]
    print('== 篇', p, key)
    for i, t in enumerate(ps):
        if t.startswith(key):
            print(' tag:', t[:50])
            print(' 譯頭:', ps[i + 1][:40])
            print(' 譯尾:', ps[i + 1][-40:])
            break
