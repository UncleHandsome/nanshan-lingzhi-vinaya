# -*- coding: utf-8 -*-
"""乾跑：把 fix_batch1.tsv 套到暫存複本，檢查段數不變、換行體例不變、差異僅在指定處。"""
import os, io, re, json, shutil

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
REV = os.path.join(B, 'AI語譯', '_work', 'review')
OUT = os.path.join(B, 'AI語譯', 'out')
TMP = os.path.join(B, 'AI語譯', '_work', 'review', '_b1', 'dry')

rows = []
for line in io.open(os.path.join(REV, 'fix_batch1.tsv'), encoding='utf-8').read().split('\n'):
    if not line:
        continue
    bk, ck, sg, new = line.split('\t')
    rows.append((bk, ck, int(sg), new.replace('\\n', '\n')))

by_chunk = {}
for bk, ck, sg, new in rows:
    by_chunk.setdefault((bk, ck), {})[sg] = new

if os.path.isdir(TMP):
    shutil.rmtree(TMP)
ok = True
for (bk, ck), segs in by_chunk.items():
    p = os.path.join(OUT, bk, ck + '.txt')
    raw = io.open(p, encoding='utf-8', newline='').read()
    crlf = '\r\n' in raw
    txt = raw.replace('\r\n', '\n')
    parts = re.split(r'\n\s*\n', txt)
    n0 = len(parts)
    for sg in segs:
        parts[sg - 1] = segs[sg]
    body = '\n\n'.join(parts)
    if crlf:
        body = body.replace('\n', '\r\n')
    d = os.path.join(TMP, bk)
    os.makedirs(d, exist_ok=True)
    io.open(os.path.join(d, ck + '.txt'), 'w', encoding='utf-8', newline='').write(body)
    # 回讀檢查
    back = io.open(os.path.join(d, ck + '.txt'), encoding='utf-8', newline='').read()
    n1 = len(re.split(r'\n\s*\n', back.replace('\r\n', '\n')))
    same_nl = ('\r\n' in back) == crlf
    print('%-12s %-14s 段數 %d→%d  CRLF=%s  改 %d 段  %s' % (
        bk, ck, n0, n1, crlf, len(segs), 'OK' if (n0 == n1 and same_nl) else '!! FAIL'))
    ok &= (n0 == n1 and same_nl)

print('全部 OK' if ok else '有問題')
