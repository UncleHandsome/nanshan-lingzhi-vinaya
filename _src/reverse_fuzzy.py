# -*- coding: utf-8 -*-
"""反向模糊：每個定稿缺口去定稿 source 找，判断是位置錯、部分、还是没有。"""
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


def han(s):
    s = re.sub(r'^(?:【[^】]+】)+', '', s.strip())
    return ''.join(re.findall(r'[\u4e00-\u9fff]', s))


def is_nonbody(t):
    t = t[:120]
    return ('No. 714' in t or 'No.714' in t or ('沙門釋' in t and '撰' in t)
            or '目錄' in t or '條目' in t or '凡例' in t
            or ('】' in t and re.search(r'卷[上中下]|卷[一二三四]', t)))


lines = ['# 五書缺口反向模糊比對', '', '| 書 | 正文缺口 | 已存在位置錯 | 部分覆蓋 | 定稿沒有 | 非正文 |', '|:--|--:|--:|--:|--:|--:|']
detail = []
for book, (name, rawp) in BOOKS.items():
    raw = io.open(os.path.join(B, rawp), encoding='utf-8').read()
    h = ''
    mp = []
    for i, c in enumerate(raw):
        if '\u4e00' <= c <= '\u9fff':
            h += c
            mp.append(i)
    rows = [json.loads(x) for x in io.open(os.path.join(C, book + '.jsonl'), encoding='utf-8') if x.strip()]
    sources = [(r.get('key'), han(r.get('source', ''))) for r in rows if r.get('source')]
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
    n_body = n_non = n_in = n_part = n_none = 0
    for a, b in gaps:
        t = raw[mp[a]:mp[a] + 120]
        g = h[a:b]
        if is_nonbody(t):
            n_non += 1
            continue
        n_body += 1
        hit = None
        for n in (24, 16, 12, 8):
            frag = g[:n]
            for k, s in sources:
                if frag in s:
                    hit = (k, s)
                    break
            if hit:
                break
        if hit:
            n_in += 1
            detail.append('| %s | %d | 已存在 | %s | %s |' % (name, b - a, hit[0], hit[1][:60]))
            continue
        # 部分：定稿 source 是否是 gap 的子串
        part = None
        for k, s in sources:
            if len(s) >= 12 and s in g:
                part = (k, s)
                break
        if part:
            n_part += 1
            detail.append('| %s | %d | 部分 | %s | %s |' % (name, b - a, part[0], part[1][:60]))
        else:
            n_none += 1
            detail.append('| %s | %d | 沒有 | — | %s |' % (name, b - a, t[:60].replace('\n', ' ')))
    lines.append('| %s | %d | %d | %d | %d | %d |' % (name, n_body, n_in, n_part, n_none, n_non))
    print(name, n_body, n_in, n_part, n_none, n_non)
lines += ['', '## 明細', '', '| 書 | 長度 | 判定 | 定稿 key | 原文／定稿 |', '|:--|--:|:--|:--|:--|'] + detail
fp = os.path.join(B, '重作材料_長段', '五書_缺口反向模糊.md')
io.open(fp, 'w', encoding='utf-8').write('\n'.join(lines))
print(fp)
