# -*- coding: utf-8 -*-
"""把卷首目錄／題署缺口標為非正文，只計正文缺口。"""
import io
import json
import os
import re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
C = os.path.join(B, '定稿')
BOOKS = {
    'xingshichao': ('行事鈔', 'TXT/01_四分律刪繁補闕行事鈔.txt'),
    'jieshu': ('戒疏', 'TXT/02_四分律含注戒本疏.txt'),
    'yeshu': ('業疏', 'TXT/03_四分律刪補隨機羯磨疏.txt'),
    'nicao': ('尼鈔', 'TXT/04_四分律比丘尼鈔.txt'),
    'yichao': ('義鈔', 'TXT/05_四分律拾毗尼義鈔.txt'),
}


def nonbody(txt):
    t = txt[:120]
    if 'No. 714' in t or 'No.714' in t:
        return True
    if '沙門釋' in t and '撰' in t:
        return True
    if '目錄' in t or '條目' in t or '凡例' in t:
        return True
    if '】' in t and re.search(r'卷[上中下]|卷[一二三四]', t):
        return True
    return False


lines = ['# 五書缺口分類', '', '| 書 | 單位 | 正文缺口 | 非正文缺口 | 重疊 |', '|:--|--:|--:|--:|--:|']
for book, (name, rawp) in BOOKS.items():
    raw = io.open(os.path.join(B, rawp), encoding='utf-8').read()
    h = ''
    mp = []
    for i, c in enumerate(raw):
        if '\u4e00' <= c <= '\u9fff':
            h += c
            mp.append(i)
    rows = [json.loads(x) for x in io.open(os.path.join(C, book + '.jsonl'), encoding='utf-8') if x.strip()]
    iv = [(r['raw_start'], r['raw_end']) for r in rows if r.get('raw_start', -1) >= 0 and r.get('raw_end', 0) > r['raw_start']]
    cover = [0] * len(h)
    for a, b in iv:
        for i in range(a, min(b, len(h))):
            cover[i] += 1
    gaps = []
    i = 0
    while i < len(h):
        if cover[i] == 0:
            j = i
            while j < len(h) and cover[j] == 0:
                j += 1
            if j - i >= 20:
                gaps.append((i, j))
            i = j
        else:
            i += 1
    body = [g for g in gaps if not nonbody(raw[mp[g[0]]:mp[g[0]] + 120])]
    other = len(gaps) - len(body)
    dups = sum(1 for a, b in iv if any(cover[i] > 1 for i in range(a, min(b, len(h)))))
    lines.append('| %s | %d | %d | %d | %d |' % (name, len(rows), len(body), other, dups))
fp = os.path.join(B, '重作材料_長段', '五書_缺口分類.md')
io.open(fp, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print('\n'.join(lines))
