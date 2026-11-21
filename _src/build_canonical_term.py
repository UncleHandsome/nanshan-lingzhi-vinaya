# -*- coding: utf-8 -*-
"""由 _終審 + 修訂回覆建立五書定稿，保留分段。"""
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


def split_labels(text):
    text = (text or '').strip()
    ms = [m for m in re.finditer(r'【([^】]+)】', text) if m.group(1) in LABELS]
    if not ms:
        return []
    out = []
    for i, m in enumerate(ms):
        end = ms[i + 1].start() if i + 1 < len(ms) else len(text)
        body = text[m.end():end].strip()
        if body:
            out.append((m.group(1), body))
    return out


def parse(md, rep):
    i = md.rfind('【原文】')
    j = md.rfind('【待審譯文】')
    if i < 0 or j < 0:
        return None
    raw_src = md[i + 4:j].strip()
    cut = min([x for x in (raw_src.find('【裁決分歧參考'), raw_src.find('【後文背景'), raw_src.find('\n---')) if x >= 0] or [len(raw_src)])
    raw_src = raw_src[:cut].strip()
    e = min([x for x in (md.find('【後文背景】', j), md.find('【裁決分歧參考', j)) if x >= 0] or [len(md)])
    tr = md[j + 6:e].strip()
    tr = tr.split('【裁決分歧參考')[0].split('【後文背景')[0].strip()
    revised = False
    if rep and os.path.exists(rep):
        tr = io.open(rep, encoding='utf-8').read().strip()
        revised = True
    marks = list(re.finditer(r'■\s*([^\n（]+)（原文）', raw_src))
    segs = []
    if marks:
        for k, m in enumerate(marks):
            end = marks[k + 1].start() if k + 1 < len(marks) else len(raw_src)
            body = raw_src[m.end():end].strip()
            label = m.group(1).strip()
            if body:
                segs.append({'label': label, 'source': body})
    if not segs:
        label = ''
        lm = re.search(r'【([^】]+)】', raw_src)
        if lm and lm.group(1) in LABELS:
            label = lm.group(1)
        body = re.sub(r'^(?:【[^】]+】)+', '', raw_src).strip()
        if body:
            segs.append({'label': label, 'source': body})
    trs = split_labels(tr)
    if len(segs) == len(trs):
        for s, t in zip(segs, trs):
            s['translation'] = t[1]
    elif len(segs) == 1:
        segs[0]['translation'] = tr
    else:
        for s in segs:
            s['translation'] = ''
    src_all = re.sub(r'■\s*[^\n（]*（原文）', '', raw_src).strip()
    return segs, src_all, tr, revised


def main():
    old = os.path.join(OUT, '_舊_頁面抽樣')
    os.makedirs(old, exist_ok=True)
    index = {'books': {}, 'total': 0, 'pairs': 0}
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
            segs, src, tr, revised = p
            rows.append({
                'book': name, 'book_id': book, 'key': key,
                'label': segs[0]['label'] if segs else '',
                'source': src, 'translation': tr, 'revised': revised,
                'segments': segs,
            })
        fp = os.path.join(OUT, book + '.jsonl')
        with io.open(fp, 'w', encoding='utf-8') as fh:
            for r in rows:
                fh.write(json.dumps(r, ensure_ascii=False) + '\n')
        pairs = sum(len(r['segments']) for r in rows)
        index['books'][book] = {'name': name, 'units': len(rows), 'revised': sum(1 for r in rows if r['revised']), 'pairs': pairs, 'file': book + '.jsonl'}
        index['total'] += len(rows)
        index['pairs'] += pairs
        print('%s units %d pairs %d revised %d' % (name, len(rows), pairs, index['books'][book]['revised']))
    with io.open(os.path.join(OUT, '索引.json'), 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    print('total', index['total'], 'pairs', index['pairs'])


if __name__ == '__main__':
    main()
