# -*- coding: utf-8 -*-
"""由 _終審 + 修訂回覆建立五書定稿；不再從 docs 抽。"""
import io
import json
import os
import re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
OUT = os.path.join(B, '定稿')
BOOKS = {
    'xingshichao': ('行事鈔', '測試/重譯/行事鈔/_終審', '測試/重譯/行事鈔/_終修/回覆'),
    'jieshu': ('戒疏', '測試/重譯/戒疏/_終審', '測試/重譯/戒疏/_終修_20261121/回覆'),
    'yeshu': ('業疏', '測試/重譯/業疏/_終審', '測試/重譯/業疏/_終修_20261121/回覆'),
    'nicao': ('尼鈔', '測試/重譯/尼鈔/_終審', '測試/重譯/尼鈔/_終修/回覆'),
    'yichao': ('義鈔', '測試/重譯/義鈔/_終審', '測試/重譯/義鈔/_終修/回覆'),
}
LABELS = ('疏文', '記文', '鈔文', '律文', '註文', '序文')


def parse(md, rep):
    i = md.rfind('【原文】')
    j = md.rfind('【待審譯文】')
    if i < 0 or j < 0:
        return None
    src = md[i + 4:j].strip()
    src = re.sub(r'■\s*[^\n（]*（原文）', '', src).strip()
    e = min([x for x in (md.find('【後文背景】', j), md.find('【裁決分歧參考', j)) if x >= 0] or [len(md)])
    tr = md[j + 6:e].strip()
    revised = False
    if rep and os.path.exists(rep):
        tr = io.open(rep, encoding='utf-8').read().strip()
        revised = True
    lm = re.search(r'■\s*([^\n（]+)（原文）', md[i:j])
    label = lm.group(1).strip() if lm else ''
    if label not in LABELS:
        lm2 = re.search(r'【([^】]+)】', src)
        label = lm2.group(1) if lm2 and lm2.group(1) in LABELS else ''
    src = re.sub(r'^(?:【[^】]+】)+', '', src).strip()
    return label, src, tr, revised


def main():
    old = os.path.join(OUT, '_舊_頁面抽樣')
    os.makedirs(old, exist_ok=True)
    for f in os.listdir(OUT):
        if f.endswith('.jsonl'):
            os.replace(os.path.join(OUT, f), os.path.join(old, f))
    index = {'books': {}, 'total': 0}
    for book, (name, termdir, revdir) in BOOKS.items():
        rows = []
        for f in sorted(os.listdir(os.path.join(B, termdir))):
            if not f.endswith('.md'):
                continue
            key = f[:-3]
            md = io.open(os.path.join(B, termdir, f), encoding='utf-8').read()
            rep = os.path.join(B, revdir, key + '_回.txt')
            p = parse(md, rep)
            if not p:
                continue
            label, src, tr, revised = p
            rows.append({'book': name, 'book_id': book, 'key': key, 'label': label, 'source': src, 'translation': tr, 'revised': revised})
        fp = os.path.join(OUT, book + '.jsonl')
        with io.open(fp, 'w', encoding='utf-8') as fh:
            for r in rows:
                fh.write(json.dumps(r, ensure_ascii=False) + '\n')
        index['books'][book] = {'name': name, 'units': len(rows), 'revised': sum(1 for r in rows if r['revised']), 'file': book + '.jsonl'}
        index['total'] += len(rows)
        print('%s %d revised %d' % (name, len(rows), index['books'][book]['revised']))
    with io.open(os.path.join(OUT, '索引.json'), 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    print('total', index['total'])


if __name__ == '__main__':
    main()
