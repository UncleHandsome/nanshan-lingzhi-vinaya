# -*- coding: utf-8 -*-
"""用定稿 source 模糊搜尋 raw 缺口，修正 raw_start。"""
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


def gaps_of(h, rows):
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
    return gaps


REPORT = ['# 定稿缺口模糊搜尋', '']
for book, (name, rawp) in BOOKS.items():
    raw = io.open(os.path.join(B, rawp), encoding='utf-8').read()
    h = ''
    mp = []
    for i, c in enumerate(raw):
        if '\u4e00' <= c <= '\u9fff':
            h += c
            mp.append(i)
    p = os.path.join(C, book + '.jsonl')
    rows = [json.loads(x) for x in io.open(p, encoding='utf-8') if x.strip()]
    before = len(gaps_of(h, rows))
    fixed = 0
    for a, b in gaps_of(h, rows):
        frag = h[a:a + 24]
        cands = []
        for r in rows:
            s = han(r.get('source', ''))
            n = s.find(frag)
            if n >= 0:
                cands.append((abs((r.get('raw_start') or 0) - a), r, n))
        if not cands:
            for size in (16, 12, 8):
                frag = h[a:a + size]
                for r in rows:
                    s = han(r.get('source', ''))
                    n = s.find(frag)
                    if n >= 0:
                        cands.append((abs((r.get('raw_start') or 0) - a), r, n))
                if cands:
                    break
        if not cands:
            continue
        cands.sort(key=lambda x: x[0])
        _, r, off = cands[0]
        r['raw_start'] = max(0, a - off)
        r['raw_end'] = r['raw_start'] + len(han(r.get('source', '')))
        fixed += 1
    after = len(gaps_of(h, rows))
    io.open(p, 'w', encoding='utf-8').writelines(json.dumps(r, ensure_ascii=False) + '\n' for r in rows)
    REPORT.append('## %s' % name)
    REPORT.append('')
    REPORT.append('- 修正前缺口：%d' % before)
    REPORT.append('- 模糊修正：%d' % fixed)
    REPORT.append('- 修正後缺口：%d' % after)
    REPORT.append('')
    print(name, before, fixed, after)
fp = os.path.join(B, '重作材料_長段', '五書_缺口模糊搜尋.md')
io.open(fp, 'w', encoding='utf-8').write('\n'.join(REPORT))
print(fp)
