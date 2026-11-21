# -*- coding: utf-8 -*-
"""定稿：同卷同原文只留一筆（優先修訂、譯文較長）。"""
import io
import json
import os
import re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
C = os.path.join(B, '定稿')
BOOKS = ('xingshichao', 'jieshu', 'yeshu', 'nicao', 'yichao')


def han(s):
    s = re.sub(r'^(?:【[^】]+】)+', '', s.strip())
    return ''.join(re.findall(r'[\u4e00-\u9fff]', s))


for book in BOOKS:
    p = os.path.join(C, book + '.jsonl')
    rows = [json.loads(x) for x in io.open(p, encoding='utf-8') if x.strip()]
    groups = {}
    for r in rows:
        groups.setdefault((r.get('vol'), han(r.get('source', ''))), []).append(r)
    keep = []
    removed = 0
    for g in groups.values():
        g.sort(key=lambda r: (1 if r.get('revised') else 0, len(r.get('translation', ''))), reverse=True)
        keep.append(g[0])
        removed += len(g) - 1
    # preserve original order by key
    keep.sort(key=lambda r: r.get('key', ''))
    io.open(p, 'w', encoding='utf-8').writelines(json.dumps(r, ensure_ascii=False) + '\n' for r in keep)
    print(book, len(rows), '->', len(keep), 'removed', removed)
