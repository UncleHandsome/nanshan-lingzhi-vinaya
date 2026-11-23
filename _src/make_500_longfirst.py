# -*- coding: utf-8 -*-
"""依原文漢字數重新準備 Qwen 材料：長段優先、每檔約 500 字。

輸出：
  六書_500字_長段優先/
    README.md
    0001.md ...
    _order.json
"""
import io
import json
import os
import re
import shutil

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
OUT = os.path.join(B, '六書_500字_長段優先')
TARGET = 500
MAX = 550
BOOKS = [
    ('xingshichao', '01_行事鈔', '行事鈔'),
    ('jieshu', '02_戒本疏行宗記', '戒本疏行宗記'),
    ('yeshu', '03_業疏', '業疏'),
    ('nicao', '04_尼鈔', '尼鈔'),
    ('yichao', '05_義鈔', '義鈔'),
    ('zhichi', '06_資持記', '資持記'),
]
HAN = re.compile(r'[\u4e00-\u9fff]')
LABELS = ('疏文', '記文', '鈔文', '律文', '註文', '序文')


def han(s):
    return len(HAN.findall(s or ''))


def block(segs, key):
    """回傳 (source_display, translation_display, labels)。"""
    labs, src, tr = [], [], []
    for s in segs:
        lab = (s.get('label') or '疏文').strip()
        if lab not in LABELS:
            lab = '疏文'
        labs.append(lab)
        ss = (s.get('display_source') or s.get('source') or '').strip()
        tt = (s.get('translation') or '').strip()
        src.append('【%s】\n%s' % (lab, ss))
        tr.append('【%s】\n%s' % (lab, tt))
    if not src:
        ss = (key.get('display_source') or key.get('source') or '').strip()
        tt = (key.get('translation') or '').strip()
        lab = (key.get('label') or '疏文').strip()
        if lab not in LABELS:
            lab = '疏文'
        labs = [lab]
        src = ['【%s】\n%s' % (lab, ss)]
        tr = ['【%s】\n%s' % (lab, tt)]
    return '\n\n'.join(src), '\n\n'.join(tr), labs


def load():
    items = []
    excl = set()
    scan = os.path.join(B, '重作材料_長段', 'source_segments_scan_20261124.json')
    if os.path.exists(scan):
        for x in json.load(io.open(scan, encoding='utf-8')):
            if x.get('category') == 'unrelated':
                excl.add((x['book'], str(x['key'])))
    for order, (bid, folder, label) in enumerate(BOOKS):
        path = os.path.join(B, '定稿', bid + '.jsonl')
        for ln in io.open(path, encoding='utf-8'):
            if not ln.strip():
                continue
            r = json.loads(ln)
            if (bid, str(r['key'])) in excl:
                continue
            segs = r.get('segments') or []
            has_tr = bool((r.get('translation') or '').strip()) or any((s.get('translation') or '').strip() for s in segs)
            if not has_tr:
                continue
            src, tr, labs = block(segs, r)
            if not src.strip() or not tr.strip():
                continue
            items.append({
                'book_id': bid,
                'book': label,
                'folder': folder,
                'key': str(r['key']),
                'src': src,
                'tr': tr,
                'labs': labs,
                'chars': han(src),
                'order': order,
            })
    items.sort(key=lambda x: (-x['chars'], x['order'], x['key']))
    return items


def prompt(book_id):
    return '''<!--
Qwen 校閱指示：
逐段檢查下面各段「白話」。只回報有問題的段，不要重寫沒問題的段。
- 每段都有 book_id、key、原文段別；只處理白話，不改原文或 key。
- 有問題：輸出該段修正後白話。請依語意自然分段，一段一個 paragraphs 元素；不要合併成一大段，也不要切碎句子。
- 沒問題：該段不要輸出。
- 只輸出 JSONL，每行一個物件：
  {"book_id":"...","key":"...","segments":[{"label":"疏文","paragraphs":["第一段","第二段"]}]}
- segments 的 label 與順序必須照該段原文；不要增加、刪除或改 label。
- 不要 code fence、不要前言、不要解釋、不要改原文。
- 若整檔全部沒問題，只回覆：NONE
-->
'''


def flush(buf, idx):
    if not buf:
        return
    chars = sum(x['chars'] for x in buf)
    lines = [
        '# 長段優先　%04d' % idx,
        '',
        '本檔 %d 段；原文 %d 字。' % (len(buf), chars),
        '',
        prompt(''),
    ]
    for x in buf:
        lines += [
            '## %s／%s（book_id=%s）' % (x['book'], x['key'], x['book_id']),
            '',
            '### 原文',
            '',
            x['src'],
            '',
            '### 白話',
            '',
            x['tr'],
            '',
            '---',
            '',
        ]
    with io.open(os.path.join(OUT, '%04d.md' % idx), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines).rstrip() + '\n')


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    items = load()
    buf, chars, idx, files = [], 0, 1, 0
    for x in items:
        if buf and chars + x['chars'] > MAX:
            flush(buf, idx); idx += 1; files += 1; buf, chars = [], 0
        buf.append(x); chars += x['chars']
        if chars >= TARGET:
            flush(buf, idx); idx += 1; files += 1; buf, chars = [], 0
    if buf:
        flush(buf, idx); files += 1
    io.open(os.path.join(OUT, '_order.json'), 'w', encoding='utf-8').write(
        json.dumps([{k: x[k] for k in ('book_id', 'book', 'key', 'chars')} for x in items],
                   ensure_ascii=False, indent=1) + '\n')
    print('files', files, 'sections', len(items), 'chars', sum(x['chars'] for x in items))
    print('OUT', OUT)


if __name__ == '__main__':
    main()
