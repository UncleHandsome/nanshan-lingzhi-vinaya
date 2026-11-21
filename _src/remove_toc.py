# -*- coding: utf-8 -*-
"""移除定稿中的目錄／條目單位。"""
import io, json, os
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
C = os.path.join(B, '定稿')
for book in ('xingshichao', 'jieshu', 'yeshu', 'nicao', 'yichao'):
    p = os.path.join(C, book + '.jsonl')
    rows = [json.loads(x) for x in io.open(p, encoding='utf-8') if x.strip()]
    keep = []
    removed = 0
    for r in rows:
        s = r.get('source', '').strip()
        if s.startswith('【目錄】') or s.startswith('【條目】') or s.startswith('【目次】'):
            removed += 1
            continue
        keep.append(r)
    io.open(p, 'w', encoding='utf-8').writelines(json.dumps(r, ensure_ascii=False) + '\n' for r in keep)
    print(book, len(rows), '->', len(keep), 'removed', removed)
