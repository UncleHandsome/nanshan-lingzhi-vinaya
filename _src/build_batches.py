# -*- coding: utf-8 -*-
"""把每卷按檔數切成 ≤25 檔的批次，輸出批次清單供派工。"""
import glob
import io
import os
import re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
W = os.path.join(B, 'AI語譯', '_work', 'review', '卷派工')
OUT = os.path.join(B, 'AI語譯', '_work', 'review', '批次派工')
REV = os.path.join(B, 'AI語譯', '_work', 'review')
LIMIT = 25

os.makedirs(OUT, exist_ok=True)
for f in glob.glob(os.path.join(OUT, '*.tsv')):
    os.remove(f)

# 已完成（有說明檔）
BOOKS = ['行事鈔', '比丘尼鈔', '拾毗尼義鈔', '戒疏', '業疏', '資持記']


def key(tag):
    k = tag.replace('_', '')
    for b in BOOKS:
        k = k.replace(b, '')
    return k


done = set()
for p in glob.glob(os.path.join(REV, '說明_7K_*.md')):
    t = os.path.basename(p)[len('說明_7K_'):-len('.md')].replace('_續', '')
    done.add(key(t))


RUNNING = {
    '02_戒疏_卷一下之二', '02_戒疏_卷二下之一', '02_戒疏_卷三上之一',
    '02_戒疏_卷三上之二', '02_戒疏_卷三下之二', '02_戒疏_卷三下之三',
    '02_戒疏_卷四上之一', '02_戒疏_卷四上之二', '02_戒疏_卷四上之三',
    '02_戒疏_卷四下之一', '02_戒疏_卷四下之二', '02_戒疏_卷四下之三',
    '02_戒疏_卷首', '03_業疏_卷一之一', '03_業疏_卷一之二', '03_業疏_卷一之三',
}

rows = []
for p in sorted(glob.glob(os.path.join(W, '*.tsv'))):
    tag = os.path.basename(p)[:-4]
    if key(tag) in done or tag in RUNNING:
        continue
    lines = [l.strip() for l in io.open(p, encoding='utf-8') if l.strip()]
    if not lines:
        continue
    book, vol = tag.split('_', 1)
    if len(lines) <= LIMIT:
        batches = [(tag, lines)]
    else:
        batches = []
        for i in range(0, len(lines), LIMIT):
            part = lines[i:i + LIMIT]
            suffix = chr(ord('a') + i // LIMIT)
            batches.append(('%s_%s' % (tag, suffix), part))
    for btag, blines in batches:
        io.open(os.path.join(OUT, btag + '.tsv'), 'w', encoding='utf-8').write('\n'.join(blines) + '\n')
        rows.append((btag, len(blines)))

print('批次總數', len(rows), '｜檔數合計', sum(r[1] for r in rows))
big = [r for r in rows if r[1] > LIMIT]
print('超過 %d 檔的批次：%d 個' % (LIMIT, len(big)))
print()
print('前 20 個批次：')
for t, n in rows[:20]:
    print('  %-32s %2d 檔' % (t, n))