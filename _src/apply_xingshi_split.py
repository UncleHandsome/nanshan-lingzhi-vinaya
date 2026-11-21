# -*- coding: utf-8 -*-
import io, json, os, shutil
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
add = [json.loads(x) for x in io.open(os.path.join(B, '重作材料_長段', '行事鈔_缺口切分.jsonl'), encoding='utf-8') if x.strip()]
p = os.path.join(B, '定稿', 'xingshichao.jsonl')
rows = [json.loads(x) for x in io.open(p, encoding='utf-8') if x.strip()]
rows = [r for r in rows if not r['key'].startswith('GAP')]
have = {(r.get('raw_start'), r.get('raw_end'), r.get('source')) for r in rows}
n = 0
for r in add:
    src, tr = r.get('source', '').strip(), r.get('translation', '').strip()
    if not src or not tr:
        continue
    k = (r.get('raw_start'), r.get('raw_end'), src)
    if k in have:
        continue
    have.add(k)
    rows.append({'book': '行事鈔', 'book_id': 'xingshichao', 'key': r.get('key', 'GAP%02d' % (n + 1)), 'label': '鈔文',
                 'source': src, 'translation': tr, 'revised': True,
                 'segments': [{'label': '鈔文', 'source': src, 'translation': tr}],
                 'raw_start': r.get('raw_start', -1), 'raw_end': r.get('raw_end', -1), 'vol': '', 'chunk': ''})
    n += 1
shutil.copy(p, os.path.join(B, '定稿', '_舊_xingshichao.jsonl'))
io.open(p, 'w', encoding='utf-8').writelines(json.dumps(x, ensure_ascii=False) + '\n' for x in rows)
print('added', n, 'rows', len(rows))
