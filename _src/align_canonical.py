# -*- coding: utf-8 -*-
"""以定稿 raw_start 做五書順序覆蓋整合。"""
import io
import json
import os

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
C = os.path.join(B, '定稿')
BOOKS = {
    'xingshichao': ('行事鈔', 'TXT/01_四分律刪繁補闕行事鈔.txt'),
    'jieshu': ('戒疏', 'TXT/02_四分律含注戒本疏.txt'),
    'yeshu': ('業疏', 'TXT/03_四分律刪補隨機羯磨疏.txt'),
    'nicao': ('尼鈔', 'TXT/04_四分律比丘尼鈔.txt'),
    'yichao': ('義鈔', 'TXT/05_四分律拾毗尼義鈔.txt'),
}


def main():
    lines = ['# 五書定稿順序對齊整合', '', '| 書 | 單位 | 有位置 | 未定位 | 缺口 | 重疊 |', '|:--|--:|--:|--:|--:|--:|']
    for book, (name, rawp) in BOOKS.items():
        raw = io.open(os.path.join(B, rawp), encoding='utf-8').read()
        h = ''
        for c in raw:
            if '\u4e00' <= c <= '\u9fff':
                h += c
        rows = [json.loads(x) for x in io.open(os.path.join(C, book + '.jsonl'), encoding='utf-8') if x.strip()]
        iv = [(r['raw_start'], r['raw_end']) for r in rows if r.get('raw_start', -1) >= 0 and r.get('raw_end', -1) > r['raw_start']]
        cover = [0] * len(h)
        for a, b in iv:
            for i in range(a, min(b, len(h))):
                cover[i] += 1
        gaps = 0
        i = 0
        while i < len(h):
            if cover[i] == 0:
                j = i
                while j < len(h) and cover[j] == 0:
                    j += 1
                if j - i >= 20:
                    gaps += 1
                i = j
            else:
                i += 1
        dups = sum(1 for a, b in iv if any(cover[i] > 1 for i in range(a, min(b, len(h)))))
        lines.append('| %s | %d | %d | %d | %d | %d |' % (name, len(rows), len(iv), len(rows) - len(iv), gaps, dups))
    fp = os.path.join(B, '重作材料_長段', '五書定稿_對齊整合.md')
    io.open(fp, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    print(fp)


if __name__ == '__main__':
    main()
