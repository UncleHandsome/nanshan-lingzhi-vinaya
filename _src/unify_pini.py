# -*- coding: utf-8 -*-
"""依原文逐 chunk 統一「毘尼／毗尼」用字。"""
import io
import os

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
OUT = os.path.join(B, 'AI語譯', 'out')
BAK = os.path.join(B, '歸檔', '毗尼統一前')

PAIRS = [
    ('01_行事鈔', 'TXT_分卷/01_行事鈔'),
    ('02_戒疏', 'TXT_分卷/02_戒疏'),
    ('03_業疏', 'TXT_分卷_標點/03_業疏'),
    ('資持記', 'TXT_分卷/資持記_細分'),
    ('04_比丘尼鈔', 'TXT_分卷/04_比丘尼鈔'),
    ('05_拾毗尼義鈔', 'TXT_分卷/05_拾毗尼義鈔'),
]

changed = 0
skipped = 0
rows = []

for book, rel in PAIRS:
    sdir = os.path.join(B, rel.replace('/', os.sep))
    odir = os.path.join(OUT, book)
    if not os.path.isdir(sdir) or not os.path.isdir(odir):
        print('跳過', book)
        continue
    for f in sorted(os.listdir(sdir)):
        if not f.endswith('.txt'):
            continue
        st = io.open(os.path.join(sdir, f), encoding='utf-8', errors='ignore').read()
        a = st.count('毘尼')
        b = st.count('毗尼')
        if a == 0 and b == 0:
            continue
        if a and b:
            skipped += 1
            rows.append((book, f, 'SKIP 原文混用', a, b))
            continue
        want, other = ('毘尼', '毗尼') if a else ('毗尼', '毘尼')
        op = os.path.join(odir, f)
        if not os.path.exists(op):
            rows.append((book, f, 'NO-OUT', a, b))
            continue
        t = io.open(op, encoding='utf-8').read()
        n = t.count(other)
        if n == 0:
            continue
        os.makedirs(BAK, exist_ok=True)
        bak = os.path.join(BAK, book + '__' + f)
        if not os.path.exists(bak):
            io.open(bak, 'w', encoding='utf-8', newline='').write(t)
        t2 = t.replace(other, want)
        io.open(op, 'w', encoding='utf-8', newline='').write(t2)
        changed += 1
        rows.append((book, f, '%s→%s' % (other, want), n, 0))

print('修改檔案數', changed, '｜原文混用跳過', skipped)
for r in rows[:20]:
    print('  %-10s %-26s %-12s %d' % r)
