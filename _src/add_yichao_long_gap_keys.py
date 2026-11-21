# -*- coding: utf-8 -*-
"""把 25 個義鈔缺口對應的 11 個長段 key 補進定稿。"""
import io, json, os, re
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
LT = os.path.join(B, '測試', '重譯', '義鈔', '_長段')
KEYS = ['00_卷首_L0005', '01a_卷上之一_L0008', '01b_卷上之一_L0001', '02a_卷上之二_L0003', '02a_卷上之二_L0010', '02a_卷上之二_L0023', '02a_卷上之二_L0028', '02b_卷上之二_L0001', '03a_卷中之一_L0010', '03a_卷中之一_L0014', '03b_卷中之一_L0001', '03b_卷中之一_L0005', '04a_卷中之二_L0005', '04a_卷中之二_L0030', '04b_卷中之二_L0001', '04b_卷中之二_L0026', '04b_卷中之二_L0030']

def han(s):
    return ''.join(re.findall(r'[\u4e00-\u9fff]', s))

def source(path):
    t = io.open(path, encoding='utf-8').read()
    m = re.search(r'■\s*[^\n（]*（原文）', t)
    if not m:
        return ''
    s = t[m.end():].strip()
    cut = re.search(r'【待審譯文】|【裁決|【後文背景】|\n---', s)
    if cut:
        s = s[:cut.start()].strip()
    return s

raw = io.open(os.path.join(B, 'TXT', '05_四分律拾毗尼義鈔.txt'), encoding='utf-8').read()
h = ''
for c in raw:
    if '\u4e00' <= c <= '\u9fff':
        h += c

p = os.path.join(B, '定稿', 'yichao.jsonl')
rows = [json.loads(x) for x in io.open(p, encoding='utf-8') if x.strip()]
have = {r['key'] for r in rows}
added = 0
for k in KEYS:
    if k in have:
        continue
    sp = os.path.join(LT, '_終審材料', k + '.md')
    fp = os.path.join(LT, '_定稿', k + '.txt')
    if not (os.path.exists(sp) and os.path.exists(fp)):
        continue
    src = source(sp)
    if not src:
        continue
    tr = io.open(fp, encoding='utf-8').read()
    lines = [x for x in tr.splitlines() if x.strip()]
    if lines and re.match(r'^【[^】]+】$', lines[0]):
        lines = lines[1:]
    tr = '\n'.join(lines).strip()
    q = h.find(han(src)[:20])
    if q < 0:
        q = h.find(han(src)[:12])
    rows.append({'book': '義鈔', 'book_id': 'yichao', 'key': 'L:' + k, 'label': '鈔文', 'source': src,
                 'translation': tr, 'revised': True, 'segments': [{'label': '鈔文', 'source': src, 'translation': tr}],
                 'raw_start': q, 'raw_end': q + len(han(src)) if q >= 0 else -1, 'vol': '', 'chunk': ''})
    added += 1
io.open(p, 'w', encoding='utf-8').writelines(json.dumps(r, ensure_ascii=False) + '\n' for r in rows)
print('added', added, 'rows', len(rows))
