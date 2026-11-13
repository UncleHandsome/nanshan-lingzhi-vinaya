# -*- coding: utf-8 -*-
"""依「說明檔存在」判定完成狀態，重建 7K 逐卷派工佇列。"""
import glob
import io
import os
import re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
W = os.path.join(B, 'AI語譯', '_work', 'review', '卷派工')
REV = os.path.join(B, 'AI語譯', '_work', 'review')

# 完成訊號：說明_7K_*.md（含 _續 後綴）
done_tags = set()
for p in glob.glob(os.path.join(REV, '說明_7K_*.md')):
    t = os.path.basename(p)[len('說明_7K_'):-len('.md')]
    t = t.replace('_續', '')
    done_tags.add(t)

# 進行中（本輪 16 支）
RUNNING = {
    '02_戒疏_卷二上之三', '02_戒疏_卷一下之一', '02_戒疏_卷一下之二',
    '02_戒疏_卷二上之一', '02_戒疏_卷二上之二', '02_戒疏_卷二下之一',
    '02_戒疏_卷二下之二', '02_戒疏_卷三上之一', '02_戒疏_卷三上之二',
    '02_戒疏_卷三上之三', '02_戒疏_卷三下之一', '02_戒疏_卷三下之二',
    '02_戒疏_卷三下之三', '02_戒疏_卷四上之一', '02_戒疏_卷四上之二',
    '02_戒疏_卷四上之三',
}

ORDER = ['01_行事鈔', '02_戒疏', '03_業疏', '04_比丘尼鈔', '05_拾毗尼義鈔', '資持記']


BOOKS = ['行事鈔', '比丘尼鈔', '拾毗尼義鈔', '戒疏', '業疏', '資持記']


def norm(tag):
    """去掉底線與書名，留下「書碼＋卷名」作為比對鍵。"""
    k = tag.replace('_', '')
    for b in BOOKS:
        k = k.replace(b, '')
    return k


done_norm = {norm(t) for t in done_tags}

rows = []
for p in sorted(glob.glob(os.path.join(W, '*.tsv'))):
    tag = os.path.basename(p)[:-4]
    n = sum(1 for l in io.open(p, encoding='utf-8') if l.strip())
    if norm(tag) in done_norm:
        st = '完成'
    elif tag in RUNNING:
        st = '進行中'
    else:
        st = '待派'
    rows.append((tag, n, st))

rows.sort(key=lambda r: (ORDER.index(r[0].split('_')[0]) if r[0].split('_')[0] in ORDER else 99, r[0]))

tot = sum(r[1] for r in rows)
cnt = {s: [r for r in rows if r[2] == s] for s in ('完成', '進行中', '待派')}

out = ['# 7K 逐卷派工佇列', '',
       '總 %d 卷 / %d 檔' % (len(rows), tot), '']
for s in ('完成', '進行中', '待派'):
    out.append('- %s：%d 卷 / %d 檔' % (s, len(cnt[s]), sum(r[1] for r in cnt[s])))
out += ['', '| 卷 | 檔數 | 狀態 |', '|:--|--:|:--|']
for t, n, s in rows:
    out.append('| %s | %d | %s |' % (t, n, s))
io.open(os.path.join(B, '佇列_7K逐卷.md'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')

print('總 %d 卷 / %d 檔' % (len(rows), tot))
for s in ('完成', '進行中', '待派'):
    print('%s：%d 卷 / %d 檔' % (s, len(cnt[s]), sum(r[1] for r in cnt[s])))
print()
print('待派（前 20）：')
for t, n, s in cnt['待派'][:20]:
    print('  %-26s %3d' % (t, n))