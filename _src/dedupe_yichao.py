# -*- coding: utf-8 -*-
"""義鈔定稿：同卷同原文只留一筆。"""
import io
import json
import os
import re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = os.path.join(B, '定稿', 'yichao.jsonl')


def han(s):
    s = re.sub(r'^(?:【[^】]+】)+', '', s.strip())
    return ''.join(re.findall(r'[\u4e00-\u9fff]', s))


rows = [json.loads(x) for x in io.open(p, encoding='utf-8') if x.strip()]
seen = set()
keep = []
removed = []
for r in rows:
    key = (r.get('vol'), han(r.get('source', '')))
    if key in seen:
        removed.append(r)
        continue
    seen.add(key)
    keep.append(r)
io.open(p, 'w', encoding='utf-8').writelines(json.dumps(r, ensure_ascii=False) + '\n' for r in keep)
print('before', len(rows), 'after', len(keep), 'removed', len(removed))
for r in removed[:20]:
    print(r.get('key'), r.get('vol'), r.get('source', '')[:50])
