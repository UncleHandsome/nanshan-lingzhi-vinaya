# -*- coding: utf-8 -*-
"""更新 docs/nav.json 中三書的章節索引，使其與已重建頁面一致。"""
import io, json, os, re, html
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = os.path.join(B, 'docs', 'nav.json')
d = json.load(io.open(p, encoding='utf-8'))
for book in d['books']:
    bid = book.get('out')
    if bid not in ('xingshichao', 'yeshu', 'nicao'):
        continue
    vols = []
    for v in book.get('vols', []):
        vp = os.path.join(B, 'docs', bid, v['v'] + '.html')
        if not os.path.exists(vp):
            vols.append(v); continue
        t = io.open(vp, encoding='utf-8').read()
        secs = [[m.group(1), html.unescape(m.group(2))] for m in re.finditer(r'<h2 class="sec" id="(p\d+)">(.*?)</h2>', t, re.S)]
        vols.append({'v': v['v'], 'secs': secs})
    book['vols'] = vols
    print(bid, [(x['v'], len(x['secs'])) for x in vols])
io.open(p, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=1) + '\n')
