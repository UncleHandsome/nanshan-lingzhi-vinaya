# -*- coding: utf-8 -*-
"""把反向模糊判定為『定稿沒有／部分』的缺口整理成 AI 材料。"""
import io
import json
import os
import re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
C = os.path.join(B, '定稿')
OUT = os.path.join(B, 'AI處理材料')
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


def nonbody(t):
    t = t[:120]
    return ('No. 714' in t or 'No.714' in t or ('沙門釋' in t and '撰' in t)
            or '目錄' in t or '條目' in t or '凡例' in t
            or ('】' in t and re.search(r'卷[上中下]|卷[一二三四]', t)))


for book, (name, rawp) in BOOKS.items():
    raw = io.open(os.path.join(B, rawp), encoding='utf-8').read()
    h = ''
    mp = []
    for i, c in enumerate(raw):
        if '\u4e00' <= c <= '\u9fff':
            h += c
            mp.append(i)
    rows = [json.loads(x) for x in io.open(os.path.join(C, book + '.jsonl'), encoding='utf-8') if x.strip()]
    sources = [(r.get('key'), han(r.get('source', '')), r.get('translation', '')) for r in rows if r.get('source')]
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
    out = ['# %s 定稿缺口材料' % name, '', '只列反向模糊判定為「定稿沒有」或「部分」的正文缺口。', '']
    n = 0
    for a, b in gaps:
        t = raw[mp[a]:mp[a] + 120]
        if nonbody(t):
            continue
        g = h[a:b]
        hit = None
        for size in (24, 16, 12, 8):
            frag = g[:size]
            for k, s, tr in sources:
                if frag in s:
                    hit = (k, s, tr)
                    break
            if hit:
                break
        if hit:
            continue
        part = None
        for k, s, tr in sources:
            if len(s) >= 12 and s in g:
                part = (k, s, tr)
                break
        n += 1
        out.append('\n## G%03d\n\n- 位置：%d–%d\n- 長度：%d\n- 判定：%s\n' % (n, a, b, b - a, '部分覆蓋' if part else '定稿沒有'))
        out.append('\n### 原文\n\n%s\n' % raw[mp[a]:mp[b]].strip())
        out.append('\n### 前文\n\n%s\n' % raw[mp[max(0, a - 200)]:mp[a]].strip()[-200:])
        out.append('\n### 後文\n\n%s\n' % raw[mp[b]:mp[min(len(h) - 1, b + 200)]].strip()[:200])
        if part:
            out.append('\n### 已知部分候選\n\nkey：%s\n\n%s\n' % (part[0], part[1][:1000]))
    fp = os.path.join(OUT, '缺口_%s.md' % name)
    io.open(fp, 'w', encoding='utf-8').write('\n'.join(out))
    print(name, n, fp)
