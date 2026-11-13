# -*- coding: utf-8 -*-
"""建立「卷 → 檔號」對照，輸出派工清單，並初始化進度表。"""
import io, os, re, glob, collections

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
SRC = os.path.join(B, '校閱_7K')
W = os.path.join(B, 'AI語譯', '_work', 'review', '卷派工')
os.makedirs(W, exist_ok=True)
for f in glob.glob(os.path.join(W, '*')):
    os.remove(f)

vol = collections.defaultdict(list)
book_of = {}
for f in sorted(os.listdir(SRC)):
    if not f.endswith('.txt'):
        continue
    n = int(re.search(r'(\d+)', f).group(1))
    t = io.open(os.path.join(SRC, f), encoding='utf-8').read()
    m = re.search(r'】([^/\n]+)/([0-9]+[a-z]?)?_?([^#\n]+)#', t)
    if not m:
        continue
    book = m.group(1)
    chunk = (m.group(2) or '') + '_' + m.group(3)
    vname = re.sub(r'[a-z]+$', '', m.group(3))
    vol[(book, vname)].append(n)
    book_of[n] = book

order = ['01_行事鈔', '02_戒疏', '03_業疏', '04_比丘尼鈔', '05_拾毗尼義鈔', '資持記']
vols = sorted(vol.items(), key=lambda kv: (order.index(kv[0][0]) if kv[0][0] in order else 99, kv[0][1]))

lines = ['# 7K 逐卷派工進度', '', '| 序 | 書 | 卷 | 檔數 | 狀態 |', '|--:|:--|:--|--:|:--|']
for i, ((book, v), files) in enumerate(vols, 1):
    tag = '%s_%s' % (book, v)
    tsv = os.path.join(W, tag.replace('/', '_') + '.tsv')
    io.open(tsv, 'w', encoding='utf-8').write('\n'.join('%d\t%s' % (n, book) for n in sorted(files)))
    lines.append('| %d | %s | %s | %d | 待派 |' % (i, book, v, len(files)))

io.open(os.path.join(B, '進度_7K逐卷.md'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print('卷數', len(vols), '｜派工清單在', W)
for i, ((b, v), fs) in enumerate(vols[:14], 1):
    print('%2d %-10s %-12s %d 檔' % (i, b, v, len(fs)))
