# -*- coding: utf-8 -*-
"""重出校閱材料：每檔約 7 KB 內文，涵蓋全部段（含最初歸檔的卷首序）。"""
import io, os, re, glob, shutil

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
OUT = os.path.join(B, '校閱_7K')
PROMPT = '幫我看看白話譯文有沒有甚麼問題'
TARGET = 7000

books = [('01_行事鈔', '01_行事鈔'), ('02_戒疏', '02_戒疏'),
         ('資持記', '資持記_細分'), ('04_比丘尼鈔', '04_比丘尼鈔'),
         ('05_拾毗尼義鈔', '05_拾毗尼義鈔')]

recs = []
for book, sd in books:
    for f in sorted(glob.glob(os.path.join(B, 'TXT_分卷', sd, '*.txt'))):
        ch = os.path.splitext(os.path.basename(f))[0]
        src = [x.strip() for x in io.open(f, encoding='utf-8').read().split('\n')[5:] if x.strip()]
        tr = [x for x in re.split(r'\r?\n\r?\n', io.open(os.path.join(B, 'AI語譯', 'out', book, ch + '.txt'), encoding='utf-8').read()) if x.strip()]
        if len(src) != len(tr):
            print('⚠ 段數不符', book, ch, len(src), len(tr))
        for i, (a, t) in enumerate(zip(src, tr)):
            recs.append((book, ch, i + 1, a, t))

for f in sorted(glob.glob(os.path.join(B, 'TXT_分卷_標點', '03_業疏', '*.txt'))):
    ch = os.path.splitext(os.path.basename(f))[0]
    src = [x.strip() for x in io.open(f, encoding='utf-8').read().split('\n') if x.strip()]
    tr = [x for x in re.split(r'\r?\n\r?\n', io.open(os.path.join(B, 'AI語譯', 'out', '03_業疏', ch + '.txt'), encoding='utf-8').read()) if x.strip()]
    if len(src) != len(tr):
        print('⚠ 段數不符 03_業疏', ch, len(src), len(tr))
    for i, (a, t) in enumerate(zip(src, tr)):
        recs.append(('03_業疏', ch, i + 1, a, t))

print('總段數', len(recs))

if os.path.isdir(OUT):
    shutil.rmtree(OUT)
os.makedirs(OUT)

n = 0
buf = []
cur = 0


def flush():
    global buf, cur, n
    if not buf:
        return
    n += 1
    head = '# 校閱材料　第%03d檔\n\n%s\n\n---\n\n# 材料開始\n\n' % (n, PROMPT)
    body = ''.join('【%03d-%04d】%s/%s#%d\n【原文】%s\n【譯文】%s\n\n'
                   % (n, k + 1, b, c, s, a, t) for k, (b, c, s, a, t) in enumerate(buf))
    io.open(os.path.join(OUT, '校閱_%03d.txt' % n), 'w', encoding='utf-8').write(head + body)
    buf = []
    cur = 0


for r in recs:
    est = len(('【000-0000】X/%s#%d\n【原文】%s\n【譯文】%s\n\n' % (r[1], r[2], r[3], r[4])).encode('utf-8'))
    if buf and cur + est > TARGET:
        flush()
    buf.append(r)
    cur += est
flush()

size = [os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT)]
print('檔數', n, '平均 KB %.1f' % (sum(size) / len(size) / 1024), '最大 KB %.1f' % (max(size) / 1024))
