# -*- coding: utf-8 -*-
"""從 docs 現頁抽出一份五書定稿 JSONL；之後所有材料／校對都從這裡拿。"""
import io
import json
import os
import re
import html

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
OUT = os.path.join(B, '定稿')
BOOKS = {
    'xingshichao': ('行事鈔', ('卷上', '卷中', '卷下'), 'TXT/01_四分律刪繁補闕行事鈔.txt'),
    'jieshu': ('戒疏', ('卷一', '卷二', '卷三', '卷四'), 'TXT/02_四分律含注戒本疏.txt'),
    'yeshu': ('業疏', ('卷一', '卷二', '卷三', '卷四'), 'TXT/03_四分律刪補隨機羯磨疏.txt'),
    'nicao': ('尼鈔', ('卷上', '卷中', '卷下'), 'TXT/04_四分律比丘尼鈔.txt'),
    'yichao': ('義鈔', ('卷上', '卷中'), 'TXT/05_四分律拾毗尼義鈔.txt'),
}
LABELS = ('疏文', '記文', '鈔文', '律文', '註文', '序文')


def han(s):
    s = re.sub(r'^(?:【[^】]+】)+', '', s.strip())
    return ''.join(re.findall(r'[\u4e00-\u9fff]', s))


def main():
    os.makedirs(OUT, exist_ok=True)
    index = {'books': {}, 'total': 0}
    for book, (name, vols, rawp) in BOOKS.items():
        raw = io.open(os.path.join(B, rawp), encoding='utf-8').read()
        h = ''
        for c in raw:
            if re.match(r'[\u4e00-\u9fff]', c):
                h += c
        rows = []
        for v in vols:
            t = io.open(os.path.join(B, 'docs', book, v + '.html'), encoding='utf-8').read()
            idx = 0
            for m in re.finditer(r'<div class="pair[^"]*"[^>]*><div class="o[^"]*">(.*?)</div><div class="t">(.*?)</div></div>', t, re.S):
                idx += 1
                o = html.unescape(re.sub('<[^>]+>', '', m.group(1))).strip()
                tr = html.unescape(re.sub('<[^>]+>', '', m.group(2))).strip()
                lm = re.match(r'【([^】]+)】', o)
                label = lm.group(1) if lm and lm.group(1) in LABELS else ''
                body = re.sub(r'^【[^】]+】', '', o).strip()
                s = han(body)
                q = h.find(s[:20]) if s else -1
                if q < 0:
                    q = h.find(s[:12]) if s else -1
                if q < 0:
                    q = h.find(s[:8]) if s else -1
                rows.append({
                    'book': name,
                    'book_id': book,
                    'vol': v,
                    'key': '%s-%03d' % (v, idx),
                    'label': label,
                    'source': body,
                    'translation': tr,
                    'raw_start': q,
                    'raw_end': (q + len(s)) if q >= 0 else -1,
                })
        fp = os.path.join(OUT, book + '.jsonl')
        with io.open(fp, 'w', encoding='utf-8') as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')
        matched = sum(1 for r in rows if r['raw_start'] >= 0)
        index['books'][book] = {'name': name, 'pairs': len(rows), 'matched': matched, 'file': book + '.jsonl'}
        index['total'] += len(rows)
        print('%s %d (matched %d)' % (name, len(rows), matched))
    with io.open(os.path.join(OUT, '索引.json'), 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    print('total', index['total'])


if __name__ == '__main__':
    main()
