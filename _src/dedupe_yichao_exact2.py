# -*- coding: utf-8 -*-
import io, json, os
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = os.path.join(B, '定稿', 'yichao.jsonl')
rows = [json.loads(x) for x in io.open(p, encoding='utf-8') if x.strip()]
seen = set()
keep = []
removed = 0
for r in rows:
    k = (r.get('raw_start'), r.get('raw_end'), r.get('source'))
    if k in seen:
        removed += 1
        continue
    seen.add(k)
    keep.append(r)
io.open(p, 'w', encoding='utf-8').writelines(json.dumps(r, ensure_ascii=False) + '\n' for r in keep)
print('before', len(rows), 'after', len(keep), 'removed', removed)
