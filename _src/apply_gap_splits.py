# -*- coding: utf-8 -*-
import io, json, os, shutil
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
MAP = {'尼鈔': ('nicao', '尼鈔'), '業疏': ('yeshu', '業疏'), '義鈔': ('yichao', '義鈔')}
for name, (book, label) in MAP.items():
    sp = os.path.join(B, '重作材料_長段', name + '_缺口切分.jsonl')
    if not os.path.exists(sp):
        continue
    add = [json.loads(x) for x in io.open(sp, encoding='utf-8') if x.strip()]
    p = os.path.join(B, '定稿', book + '.jsonl')
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
        rows.append({'book': label, 'book_id': book, 'key': r.get('key', 'GAP%02d' % (n + 1)), 'label': '鈔文',
                     'source': src, 'translation': tr, 'revised': True,
                     'segments': [{'label': '鈔文', 'source': src, 'translation': tr}],
                     'raw_start': r.get('raw_start', -1), 'raw_end': r.get('raw_end', -1), 'vol': '', 'chunk': ''})
        n += 1
    shutil.copy(p, os.path.join(B, '定稿', '_舊_' + book + '.jsonl'))
    io.open(p, 'w', encoding='utf-8').writelines(json.dumps(x, ensure_ascii=False) + '\n' for x in rows)
    print(name, 'added', n, 'rows', len(rows))
