# -*- coding: utf-8 -*-
"""戒疏定稿：同 raw_start 只留最佳一筆。"""
import io
import json
import os

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = os.path.join(B, '定稿', 'jieshu.jsonl')
rows = [json.loads(x) for x in io.open(p, encoding='utf-8') if x.strip()]
groups = {}
for r in rows:
    k = r.get('raw_start', -1)
    groups.setdefault(k, []).append(r)
keep = []
removed = 0
for k, g in groups.items():
    if len(g) == 1:
        keep.append(g[0])
        continue
    g.sort(key=lambda r: (1 if r.get('revised') else 0, len(r.get('source', '')), len(r.get('translation', ''))), reverse=True)
    keep.append(g[0])
    removed += len(g) - 1
keep.sort(key=lambda r: r.get('key', ''))
io.open(p, 'w', encoding='utf-8').writelines(json.dumps(r, ensure_ascii=False) + '\n' for r in keep)
print('rows', len(rows), 'keep', len(keep), 'removed', removed)
