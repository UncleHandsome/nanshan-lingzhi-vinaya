# -*- coding: utf-8 -*-
"""義鈔：用多個頁面小 pair 合併補缺口。"""
import io, json, os, re, html
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
raw = io.open(os.path.join(B, 'TXT', '05_四分律拾毗尼義鈔.txt'), encoding='utf-8').read()
h = ''
mp = []
for i, c in enumerate(raw):
    if '\u4e00' <= c <= '\u9fff':
        h += c
        mp.append(i)
rows = [json.loads(x) for x in io.open(os.path.join(B, '定稿', 'yichao.jsonl'), encoding='utf-8') if x.strip()]
rows = [r for r in rows if not r['key'].startswith('GAP') and not r['key'].startswith('L:')]
pages = []
for v in ('卷上', '卷中'):
    t = io.open(os.path.join(B, 'docs', 'yichao', v + '.html'), encoding='utf-8').read()
    for m in re.finditer(r'<div class="pair[^"]*"><div class="o[^"]*">(.*?)</div><div class="t">(.*?)</div></div>', t, re.S):
        o = html.unescape(re.sub('<[^>]+>', '', m.group(1)))
        tr = html.unescape(re.sub('<[^>]+>', '', m.group(2)))
        s = ''.join(re.findall(r'[\u4e00-\u9fff]', o))
        q = h.find(s[:20])
        if q < 0:
            q = h.find(s[:12])
        if q >= 0:
            pages.append((q, q + len(s), tr))
pages.sort()
iv = [(r['raw_start'], r['raw_end']) for r in rows if r.get('raw_start', -1) >= 0]
cover = [0] * len(h)
for a, b in iv:
    for i in range(a, min(b, len(h))):
        cover[i] += 1
gaps = []
i = 0
while i < len(h):
    if cover[i] == 0:
        j = i
        while j < len(h) and cover[j] == 0:
            j += 1
        if j - i >= 20:
            gaps.append((i, j))
        i = j
    else:
        i += 1
added = 0
for a, b in gaps:
    sel = [p for p in pages if p[0] < b and a < p[1]]
    if not sel:
        continue
    cov = [0] * (b - a)
    for x, y, tr in sel:
        for i in range(max(a, x), min(b, y)):
            cov[i - a] = 1
    if sum(cov) < (b - a) * 0.8:
        continue
    tr = '\n'.join(x[2] for x in sel)
    src = raw[mp[a]:mp[b]].strip()
    rows.append({'book': '義鈔', 'book_id': 'yichao', 'key': 'GAP%02d' % (added + 1), 'label': '鈔文',
                 'source': src, 'translation': tr, 'revised': False,
                 'segments': [{'label': '鈔文', 'source': src, 'translation': tr}],
                 'raw_start': a, 'raw_end': b, 'vol': '', 'chunk': ''})
    added += 1
p = os.path.join(B, '定稿', 'yichao.jsonl')
io.open(p, 'w', encoding='utf-8').writelines(json.dumps(r, ensure_ascii=False) + '\n' for r in rows)
print('rows', len(rows), 'gaps', len(gaps), 'added', added)
