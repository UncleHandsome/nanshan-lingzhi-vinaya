import os, glob
from docx import Document

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\白話'
checks = [
    ('會本_篇16_懺六聚法.docx', '後一人法。可解。'),
    ('會本_篇16_懺六聚法.docx', '須知心斷，當日可還'),
    ('會本_篇24_導俗化方.docx', '乍觀語勢，似總一篇'),
    ('會本_篇27_諸雜要行.docx', '次料。如〈標宗〉具釋。'),
    ('會本_篇27_諸雜要行.docx', '不淨，謂宿觸等'),
    ('會本_篇26_瞻病送終.docx', '若禪師者云'),
]
for fn, needle in checks:
    fp = os.path.join(B, fn)
    if not os.path.exists(fp):
        print('缺', fn)
        continue
    ps = [p.text.strip() for p in Document(fp).paragraphs]
    hit = None
    for i, t in enumerate(ps):
        if needle in t:
            hit = i
            break
    if hit is None:
        print('[無此句]', fn, needle[:14])
    else:
        nxt = ps[hit + 1] if hit + 1 < len(ps) else ''
        print('[%s] %s | 下一段: %s' % ('譯' if any(c in nxt for c in '的是這了也') else '疑未譯', needle[:14], nxt[:36]))
