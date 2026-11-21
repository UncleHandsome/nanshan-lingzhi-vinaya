# -*- coding: utf-8 -*-
"""vol/chunk：key 有卷名就用 key，沒有才用 raw 卷題。"""
import io
import json
import os
import re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
OUT = os.path.join(B, '定稿')
BOOKS = {
    'xingshichao': ('TXT/01_四分律刪繁補闕行事鈔.txt', ('卷上', '卷中', '卷下'), r'卷[上中下](?:之[一二三四])?】'),
    'jieshu': ('TXT/02_四分律含注戒本疏.txt', ('卷一', '卷二', '卷三', '卷四'), r'卷[一二三四](?:[上下])?之?[一二三四]?】'),
    'yeshu': ('TXT/03_四分律刪補隨機羯磨疏.txt', ('卷一', '卷二', '卷三', '卷四'), r'卷[一二三四](?:之[一二三四])?】'),
    'nicao': ('TXT/04_四分律比丘尼鈔.txt', ('卷上', '卷中', '卷下'), r'卷[上中下](?:之[上中下])?】'),
    'yichao': ('TXT/05_四分律拾毗尼義鈔.txt', ('卷上', '卷中'), r'卷[上中下](?:之[一二三四])?】'),
}


def main():
    for book, (rawp, vols, pat) in BOOKS.items():
        raw = io.open(os.path.join(B, rawp), encoding='utf-8').read()
        marks = []
        for m in re.finditer(pat, raw):
            txt = m.group(0)[:-1]
            vol = re.match(r'卷[上中下]|卷[一二三四]', txt).group(0)
            marks.append((m.start(), vol, txt))
        marks.sort()
        p = os.path.join(OUT, book + '.jsonl')
        rows = [json.loads(x) for x in io.open(p, encoding='utf-8') if x.strip()]
        for r in rows:
            key = r.get('key', '')
            chunk = key.rsplit('_', 1)[0] if '_' in key else ''
            vol = ''
            for v in vols:
                if v in chunk:
                    vol = v
                    break
            if not vol:
                q = r.get('raw_start', -1)
                if q >= 0:
                    last = None
                    for pos, mv, txt in marks:
                        if pos <= q:
                            last = (mv, txt)
                        else:
                            break
                    if last:
                        vol = last[0]
                        chunk = last[1]
            r['vol'] = vol or '未定位'
            r['chunk'] = chunk or r['vol']
        # 未定位者用前後條的卷補
        last = ''
        for r in rows:
            if r['vol'] != '未定位':
                last = r['vol']
            elif last:
                r['vol'] = last
                r['chunk'] = last
        nxt = ''
        for r in reversed(rows):
            if r['vol'] != '未定位':
                nxt = r['vol']
            elif nxt:
                r['vol'] = nxt
                r['chunk'] = nxt
        with io.open(p, 'w', encoding='utf-8') as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')
        print(book, {v: sum(1 for r in rows if r['vol'] == v) for v in vols + ('未定位',)})


if __name__ == '__main__':
    main()
