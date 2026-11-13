# -*- coding: utf-8 -*-
"""套用 測試/否決錯誤_待修.tsv 的修正。

每列的 old/new 可能以「；」分隔多組，逐組套用。
"""
import io
import os
import re
import sys

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
TSV = os.path.join(B, '測試', '否決錯誤_待修.tsv')
OUT = os.path.join(B, 'AI語譯', 'out')
BAK = os.path.join(B, '歸檔', '否決錯誤修正前')
LOG = os.path.join(B, '測試', '否決錯誤_套用紀錄.md')

os.makedirs(BAK, exist_ok=True)

rows = []
for line in io.open(TSV, encoding='utf-8').read().split('\n'):
    if not line.strip() or line.startswith('書\t'):
        continue
    f = line.split('\t')
    if len(f) < 8:
        continue
    rows.append(f)

ok = 0
fail = []
log = ['# 否決錯誤套用紀錄', '']

for book, chunkfull, segid, kind, issue, old, new, status in rows:
    # chunkfull 形如 02a_卷一上之二#86 → chunk = 02a_卷一上之二
    chunk = chunkfull.split('#')[0]
    path = os.path.join(OUT, book, chunk + '.txt')
    if not os.path.exists(path):
        fail.append((segid, '找不到檔案 ' + path))
        continue
    t = io.open(path, encoding='utf-8').read()
    orig = t

    olds = [x.strip() for x in old.split('；') if x.strip()]
    news = [x.strip() for x in new.split('；')] if new.strip() else []
    # new 的組數可能少於 old（例如刪除），對齊處理
    if len(news) < len(olds):
        news += [''] * (len(olds) - len(news))

    applied = 0
    for o, n in zip(olds, news):
        o = o.strip('「」『』 ')
        if not o:
            continue
        cnt = t.count(o)
        if cnt == 1:
            t = t.replace(o, n)
            applied += 1
        elif cnt > 1:
            # 多次出現：只在第一處替換
            t = t.replace(o, n, 1)
            applied += 1
        else:
            fail.append((segid, '找不到 old：' + o[:30]))

    if t != orig:
        bak = os.path.join(BAK, book + '__' + chunk + '.txt')
        if not os.path.exists(bak):
            io.open(bak, 'w', encoding='utf-8', newline='').write(orig)
        io.open(path, 'w', encoding='utf-8', newline='').write(t)
        ok += 1
        log.append('- **%s**（%s/%s）套用 %d 組' % (segid, book, chunk, applied))
    else:
        log.append('- **%s**（%s/%s）未變更' % (segid, book, chunk))

io.open(LOG, 'w', encoding='utf-8').write('\n'.join(log) + '\n')
print('成功套用 %d 列，失敗 %d 項' % (ok, len(fail)))
for s, m in fail:
    print('  ✗ %s：%s' % (s, m))
