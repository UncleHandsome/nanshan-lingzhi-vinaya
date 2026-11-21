# -*- coding: utf-8 -*-
"""依原書卷題標記補 vol / chunk。"""
import io
import json
import os
import re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
OUT = os.path.join(B, '定稿')
BOOKS = {
    'xingshichao': ('TXT/01_四分律刪繁補闕行事鈔.txt', r'卷[上中下](?:之[一二三四])?】'),
    'jieshu': ('TXT/02_四分律含注戒本疏.txt', r'卷[一二三四](?:[上下])?之?[一二三四]?】'),
    'yeshu': ('TXT/03_四分律刪補隨機羯磨疏.txt', r'卷[一二三四](?:之[一二三四])?】'),
    'nicao': ('TXT/04_四分律比丘尼鈔.txt', r'卷[上中下](?:之[上中下])?】'),
    'yichao': ('TXT/05_四分律拾毗尼義鈔.txt', r'卷[上中下](?:之[一二三四])?】'),
}


def main():
    for book, (rawp, pat) in BOOKS.items():
        raw = io.open(os.path.join(B, rawp), encoding='utf-8').read()
        marks = []
        for m in re.finditer(pat, raw):
            txt = m.group(0)[:-1]
            vol = re.match(r'卷[上中下]|卷[一二三四]', txt).group(0)
            marks.append((m.start(), vol, txt))
        marks.sort()
        print(book, 'marks', marks[:6], '...', len(marks))
        p = os.path.join(OUT, book + '.jsonl')
        rows = [json.loads(x) for x in io.open(p, encoding='utf-8') if x.strip()]
        for r in rows:
            q = r.get('raw_start', -1)
            if q < 0:
                r['vol'] = '未定位'
                r['chunk'] = '未定位'
                continue
            last = None
            for pos, vol, txt in marks:
                if pos <= q:
                    last = (vol, txt)
                else:
                    break
            if last:
                r['vol'] = last[0]
                r['chunk'] = last[1]
            else:
                r['vol'] = '未定位'
                r['chunk'] = '未定位'
        with io.open(p, 'w', encoding='utf-8') as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')
        print(book, {v: sum(1 for r in rows if r['vol'] == v) for v in ('卷上', '卷中', '卷下', '卷一', '卷二', '卷三', '卷四', '未定位') if any(r['vol'] == v for r in rows)})


if __name__ == '__main__':
    main()
