# -*- coding: utf-8 -*-
"""掃描「譯文仍是文言」的段落：現行譯文與原文相似度過高。

用於抓落改事故（整段被換回原文）。
"""
import difflib
import io
import os
import re
import sys

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
OUT = os.path.join(B, 'AI語譯', 'out')
REPORT = os.path.join(B, '測試', '文言殘留掃描.md')

SRC = {
    '01_行事鈔': 'TXT_分卷/01_行事鈔',
    '02_戒疏': 'TXT_分卷/02_戒疏',
    '03_業疏': 'TXT_分卷_標點/03_業疏',
    '04_比丘尼鈔': 'TXT_分卷/04_比丘尼鈔',
    '05_拾毗尼義鈔': 'TXT_分卷/05_拾毗尼義鈔',
    '資持記': 'TXT_分卷/資持記_細分',
}

MIN_SRC = 40      # 原文至少 40 字才判
RATIO = 0.90      # 相似度門檻

hits = []
for book, rel in SRC.items():
    sd = os.path.join(B, rel.replace('/', os.sep))
    od = os.path.join(OUT, book)
    if not (os.path.isdir(sd) and os.path.isdir(od)):
        continue
    for f in sorted(os.listdir(sd)):
        if not f.endswith('.txt'):
            continue
        sp = os.path.join(sd, f)
        tp = os.path.join(od, f)
        if not os.path.exists(tp):
            continue
        raw = io.open(sp, encoding='utf-8', errors='ignore').read().split('\n')
        src = [x.strip() for x in (raw[5:] if book != '03_業疏' else raw) if x.strip()]
        tr = [x for x in re.split(r'\r?\n\r?\n', io.open(tp, encoding='utf-8', errors='ignore').read()) if x.strip()]
        if len(src) != len(tr):
            continue
        for i, (a, b) in enumerate(zip(src, tr), 1):
            if len(a) < MIN_SRC:
                continue
            r = difflib.SequenceMatcher(None, a, b).ratio()
            if r >= RATIO:
                hits.append((book, f[:-4], i, round(r, 3), len(a), b[:60]))

lines = ['# 文言殘留掃描（譯文與原文相似度 ≥ %.2f）' % RATIO, '',
         '共 %d 段' % len(hits), '']
for book, chunk, i, r, ln, sample in hits:
    lines.append('- **%s/%s #%d** 相似度 %.3f（原文 %d 字）｜%s' % (book, chunk, i, r, ln, sample))
os.makedirs(os.path.dirname(REPORT), exist_ok=True)
io.open(REPORT, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')

print('命中', len(hits), '段，報告', REPORT)
for h in hits[:30]:
    print('  %-10s %-22s #%-4d %.3f  %s' % (h[0], h[1][:20], h[2], h[3], h[5][:40]))