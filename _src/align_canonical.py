# -*- coding: utf-8 -*-
"""以定稿 raw_start 做五書順序覆蓋整合；非正文缺口不計入正文缺口。"""
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


def nonbody(t):
    t = t[:140]
    if t.startswith(('大覺慈父', '九十單提法', '百眾學法', '四分戒本》者',
                     '甞聞毗尼藏', '原夫大雄', '疏卷第一')):
        return True
    if '【四分律' in t[:80] and '卷' in t[:100]:
        return True
    if '四分律含注戒本疏卷' in t[:50] or '行宗記卷' in t[:60]:
        return True
    if re.match(r'^[一二三四五六七八九十百]+[^。]{0,30}戒', t):
        return True
    if t.startswith(('四分律刪補', '四分律含注', '四分律拾毗尼', '四分律比丘尼鈔', '南山三大部', '底本')):
        return True
    if '篇第' in t[:80] and ('】' in t[:80] or '卷' in t[:60]):
        return True
    return False


def main():
    lines = ['# 五書定稿順序對齊整合', '',
             '| 書 | 單位 | 有位置 | 未定位 | 正文缺口 | 非正文（已排除） | 重疊 |',
             '|:--|--:|--:|--:|--:|--:|--:|']
    for book, (name, rawp) in BOOKS.items():
        raw = io.open(os.path.join(B, rawp), encoding='utf-8').read()
        h = ''
        mp = []
        for i, c in enumerate(raw):
            if '\u4e00' <= c <= '\u9fff':
                h += c
                mp.append(i)
        rows = [json.loads(x) for x in io.open(os.path.join(C, book + '.jsonl'), encoding='utf-8') if x.strip()]
        iv = [(r['raw_start'], r['raw_end']) for r in rows if r.get('raw_start', -1) >= 0 and r.get('raw_end', -1) > r['raw_start']]
        cover = [0] * len(h)
        for a, b in iv:
            for i in range(a, min(b, len(h))):
                cover[i] += 1
        body = other = 0
        i = 0
        while i < len(h):
            if cover[i] == 0:
                j = i
                while j < len(h) and cover[j] == 0:
                    j += 1
                if j - i >= 20:
                    if nonbody(raw[mp[i]:mp[i] + 140]):
                        other += 1
                    else:
                        body += 1
                i = j
            else:
                i += 1
        dups = sum(1 for a, b in iv if any(cover[i] > 1 for i in range(a, min(b, len(h)))))
        lines.append('| %s | %d | %d | %d | %d | %d | %d |' % (name, len(rows), len(iv), len(rows) - len(iv), body, other, dups))
    lines += ['', '非正文＝卷首、序文、目次、卷題、篇題；已排除，不列為待補缺口。']
    fp = os.path.join(B, '重作材料_長段', '五書定稿_對齊整合.md')
    io.open(fp, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    print(fp)


if __name__ == '__main__':
    main()
