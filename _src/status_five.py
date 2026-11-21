# -*- coding: utf-8 -*-
import io, json, os
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
BOOKS = {'xingshichao': '行事鈔', 'jieshu': '戒疏', 'yeshu': '業疏', 'nicao': '尼鈔', 'yichao': '義鈔'}
for b, n in BOOKS.items():
    rows = [json.loads(x) for x in io.open(os.path.join(B, '定稿', b + '.jsonl'), encoding='utf-8') if x.strip()]
    pairs = sum(len(r.get('segments') or []) for r in rows)
    print(n, 'units', len(rows), 'pairs', pairs)
