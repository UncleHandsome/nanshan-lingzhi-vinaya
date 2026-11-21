# -*- coding: utf-8 -*-
"""尼鈔：用 TXT_句讀/04_尼鈔 的標點原文補 display_source，不改 source。"""
import io, json, os, re
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
b = io.open(os.path.join(B, 'TXT_句讀', '04_尼鈔', '00_全書_整理.txt'), encoding='utf-8').read()
hb = ''; mb = []
for i, c in enumerate(b):
    if '\u4e00' <= c <= '\u9fff':
        hb += c; mb.append(i)
p = os.path.join(B, '定稿', 'nicao.jsonl')
rows = [json.loads(x) for x in io.open(p, encoding='utf-8') if x.strip()]
hit = 0
for r in rows:
    s = ''.join(re.findall(r'[\u4e00-\u9fff]', r.get('source', '')))
    if not s:
        continue
    q = hb.find(s)
    if q >= 0:
        r['display_source'] = b[mb[q]:mb[q + len(s) - 1] + 1]
        hit += 1
io.open(p, 'w', encoding='utf-8').writelines(json.dumps(r, ensure_ascii=False) + '\n' for r in rows)
print('rows', len(rows), 'display', hit)
