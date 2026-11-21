# -*- coding: utf-8 -*-
"""為定稿補 vol / chunk。"""
import io
import json
import os
import re
import html

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
OUT = os.path.join(B, '定稿')
BOOKS = {
    'xingshichao': ('卷上', '卷中', '卷下'),
    'jieshu': ('卷一', '卷二', '卷三', '卷四'),
    'yeshu': ('卷一', '卷二', '卷三', '卷四'),
    'nicao': ('卷上', '卷中', '卷下'),
    'yichao': ('卷上', '卷中'),
}
RAW = {
    'xingshichao': 'TXT/01_四分律刪繁補闕行事鈔.txt',
    'jieshu': 'TXT/02_四分律含注戒本疏.txt',
    'yeshu': 'TXT/03_四分律刪補隨機羯磨疏.txt',
    'nicao': 'TXT/04_四分律比丘尼鈔.txt',
    'yichao': 'TXT/05_四分律拾毗尼義鈔.txt',
}


def han(s):
    s = re.sub(r'^(?:【[^】]+】)+', '', s.strip())
    return ''.join(re.findall(r'[\u4e00-\u9fff]', s))


def main():
    for book, vols in BOOKS.items():
        raw = io.open(os.path.join(B, RAW[book]), encoding='utf-8').read()
        h = ''
        for c in raw:
            if re.match(r'[\u4e00-\u9fff]', c):
                h += c
        # current page volume ranges
        ranges = []
        for v in vols:
            t = io.open(os.path.join(B, 'docs', book, v + '.html'), encoding='utf-8').read()
            ps = []
            for m in re.finditer(r'<div class="pair[^"]*"><div class="o[^"]*">(.*?)</div>', t, re.S):
                s = han(html.unescape(re.sub('<[^>]+>', '', m.group(1))))
                if s:
                    q = h.find(s[:20])
                    if q < 0:
                        q = h.find(s[:12])
                    if q < 0:
                        q = h.find(s[:8])
                    if q >= 0:
                        ps.append(q)
            ranges.append((min(ps) if ps else 0, max(ps) if ps else 0))
        p = os.path.join(OUT, book + '.jsonl')
        rows = [json.loads(x) for x in io.open(p, encoding='utf-8') if x.strip()]
        for r in rows:
            key = r.get('key', '')
            chunk = ''
            if '_' in key:
                chunk = key.rsplit('_', 1)[0]
            vol = ''
            for v in vols:
                if v in chunk:
                    vol = v
                    break
            if not vol:
                q = r.get('raw_start', -1)
                if q >= 0:
                    best = min(range(len(vols)), key=lambda i: min(abs(q - ranges[i][0]), abs(q - ranges[i][1])))
                    vol = vols[best]
                    chunk = chunk or vol
                else:
                    vol = '未定位'
                    chunk = chunk or vol
            r['vol'] = vol
            r['chunk'] = chunk or vol
        with io.open(p, 'w', encoding='utf-8') as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')
        print(book, len(rows), {v: sum(1 for r in rows if r['vol'] == v) for v in vols + ('未定位',)})


if __name__ == '__main__':
    main()
