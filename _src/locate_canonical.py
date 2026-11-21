# -*- coding: utf-8 -*-
"""為定稿 JSONL 補 raw_start/raw_end，含模糊定位。"""
import io
import json
import os
import re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
OUT = os.path.join(B, '定稿')
BOOKS = {
    'xingshichao': 'TXT/01_四分律刪繁補闕行事鈔.txt',
    'jieshu': 'TXT/02_四分律含注戒本疏.txt',
    'yeshu': 'TXT/03_四分律刪補隨機羯磨疏.txt',
    'nicao': 'TXT/04_四分律比丘尼鈔.txt',
    'yichao': 'TXT/05_四分律拾毗尼義鈔.txt',
}


def han(s):
    s = re.sub(r'^(?:【[^】]+】)+', '', s.strip())
    return ''.join(re.findall(r'[\u4e00-\u9fff]', s))


def locate(h, s):
    if not s:
        return -1
    for n in (20, 12, 8):
        q = h.find(s[:n])
        if q >= 0:
            return q
    # 模糊：取中段 8/6 字，回推起點
    for n in (8, 6):
        for start in (0, max(0, len(s) // 4), max(0, len(s) // 2)):
            frag = s[start:start + n]
            if len(frag) < n:
                continue
            q = h.find(frag)
            if q >= 0:
                return max(0, q - start)
    return -1


def main():
    for book, rawp in BOOKS.items():
        raw = io.open(os.path.join(B, rawp), encoding='utf-8').read()
        h = ''
        for c in raw:
            if re.match(r'[\u4e00-\u9fff]', c):
                h += c
        p = os.path.join(OUT, book + '.jsonl')
        rows = [json.loads(x) for x in io.open(p, encoding='utf-8') if x.strip()]
        miss = 0
        for r in rows:
            s = han(r.get('source', ''))
            q = locate(h, s)
            r['raw_start'] = q
            r['raw_end'] = q + len(s) if q >= 0 else -1
            if q < 0:
                miss += 1
        with io.open(p, 'w', encoding='utf-8') as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')
        print('%s rows=%d miss=%d' % (book, len(rows), miss))


if __name__ == '__main__':
    main()
