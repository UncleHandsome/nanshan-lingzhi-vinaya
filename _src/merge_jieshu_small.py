# -*- coding: utf-8 -*-
"""戒疏：G 小段優先；大單位若被 G 完整覆蓋則移除，部分覆蓋保留。"""
import io
import json
import os
import re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = os.path.join(B, '定稿', 'jieshu.jsonl')
rows = [json.loads(x) for x in io.open(p, encoding='utf-8') if x.strip()]


def is_g(r):
    return bool(re.match(r'^G\d+', r.get('key', '')))


small = [(r['raw_start'], r['raw_end']) for r in rows if is_g(r) and r.get('raw_start', -1) >= 0 and r.get('raw_end', 0) > r['raw_start']]
# union coverage of small
cover = set()
for a, b in small:
    cover.update(range(a, b))
keep = []
removed_full = kept_partial = 0
for r in rows:
    if is_g(r):
        keep.append(r)
        continue
    a, b = r.get('raw_start', -1), r.get('raw_end', -1)
    if a < 0 or b <= a:
        keep.append(r)
        continue
    n = sum(1 for x in range(a, b) if x in cover)
    if n >= (b - a) * 0.98:
        removed_full += 1
        continue
    if n:
        kept_partial += 1
    keep.append(r)
io.open(p, 'w', encoding='utf-8').writelines(json.dumps(r, ensure_ascii=False) + '\n' for r in keep)
print('rows', len(rows), 'keep', len(keep), 'removed_full', removed_full, 'kept_partial', kept_partial)
