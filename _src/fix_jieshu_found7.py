# -*- coding: utf-8 -*-
import io, json, os, re
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
raw = io.open(os.path.join(B, 'TXT', '02_四分律含注戒本疏.txt'), encoding='utf-8').read()
h = ''
mp = []
for i, c in enumerate(raw):
    if '\u4e00' <= c <= '\u9fff':
        h += c
        mp.append(i)
MAP = {
 '216489-216518': '10d_卷三上之一_0151',
 '217846-217878': '11a_卷三上之二_0025',
 '218881-218922': '11a_卷三上之二_0042',
 '278099-278120': '15a_卷三下之三_0085',
 '361495-361522': '19b_卷四下之一_0107',
 '370610-370631': '19d_卷四下之一_0039',
 '378304-378327': '20a_卷四下之二_0110',
}
p = os.path.join(B, '定稿', 'jieshu.jsonl')
rows = [json.loads(x) for x in io.open(p, encoding='utf-8') if x.strip()]
have = {(r.get('raw_start'), r.get('raw_end')) for r in rows}
for rng, key in MAP.items():
    a, b = map(int, rng.split('-'))
    if (a, b) in have:
        continue
    md = io.open(os.path.join(B, '測試', '重譯', '戒疏', '_終審', key + '.md'), encoding='utf-8').read()
    j = md.rfind('【待審譯文】')
    tr = md[j + 6:].strip() if j >= 0 else ''
    cut = re.search(r'【後文背景|【裁決|\n---', tr)
    if cut:
        tr = tr[:cut.start()].strip()
    fp = os.path.join(B, '測試', '重譯', '戒疏', '_定稿', key + '.txt')
    if os.path.exists(fp):
        tr = io.open(fp, encoding='utf-8').read()
    lines = [x for x in tr.splitlines() if x.strip()]
    if lines and re.match(r'^【[^】]+】$', lines[0]):
        lines = lines[1:]
    tr = '\n'.join(lines).strip()
    if not tr:
        continue
    src = raw[mp[a]:mp[b]].strip()
    rows.append({'book': '戒疏', 'book_id': 'jieshu', 'key': 'FIX-' + key, 'label': '疏文',
                 'source': src, 'translation': tr, 'revised': True,
                 'segments': [{'label': '疏文', 'source': src, 'translation': tr}],
                 'raw_start': a, 'raw_end': b, 'vol': '', 'chunk': ''})
io.open(p, 'w', encoding='utf-8').writelines(json.dumps(r, ensure_ascii=False) + '\n' for r in rows)
print('rows', len(rows))
