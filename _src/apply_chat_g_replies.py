# -*- coding: utf-8 -*-
"""把對話抽出的戒疏 G 回覆解析進定稿。"""
import io
import json
import os
import re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
D = os.path.join(B, '對話回覆', '已辨識')
raw = io.open(os.path.join(B, 'TXT', '02_四分律含注戒本疏.txt'), encoding='utf-8').read()
h = ''
for c in raw:
    if '\u4e00' <= c <= '\u9fff':
        h += c


def han(s):
    s = re.sub(r'^(?:【[^】]+】)+', '', s.strip())
    return ''.join(re.findall(r'[\u4e00-\u9fff]', s))


def parse_file(path):
    t = io.open(path, encoding='utf-8').read()
    out = []
    for gm in re.finditer(r'^## (G\d+)\s*\n(.*?)(?=^## G|\Z)', t, re.M | re.S):
        key = gm.group(1)
        block = gm.group(2)
        segs = []
        for sm in re.finditer(r'^### \d+\s*\n(.*?)(?=^### |\Z)', block, re.M | re.S):
            lines = [x.strip() for x in sm.group(1).splitlines() if x.strip()]
            entries = []
            for line in lines:
                m = re.match(r'【([^】]+)】(.*)', line)
                if m:
                    entries.append((m.group(1), m.group(2).strip()))
            for i in range(0, len(entries) - 1, 2):
                lab, src = entries[i]
                lab2, tr = entries[i + 1]
                if src and tr:
                    segs.append({'label': lab, 'source': src, 'translation': tr})
            if len(entries) == 1:
                segs.append({'label': entries[0][0], 'source': entries[0][1], 'translation': ''})
        if segs:
            out.append((key, segs))
    return out


items = []
for f in ('戒疏_缺口回覆_01.md', '戒疏_缺口回覆_02.md', '戒疏_缺口回覆_03.md'):
    items += parse_file(os.path.join(D, f))
print('parsed', len(items))

p = os.path.join(B, '定稿', 'jieshu.jsonl')
rows = [json.loads(x) for x in io.open(p, encoding='utf-8') if x.strip()]
have = {r['key'] for r in rows}
added = 0
for key, segs in items:
    if key in have:
        continue
    src = '\n'.join(s['source'] for s in segs)
    tr = '\n'.join(s['translation'] for s in segs)
    q = -1
    s0 = han(src)
    for n in (20, 12, 8):
        q = h.find(s0[:n])
        if q >= 0:
            break
    rows.append({'book': '戒疏', 'book_id': 'jieshu', 'key': key, 'label': segs[0]['label'],
                 'source': src, 'translation': tr, 'revised': True, 'segments': segs,
                 'raw_start': q, 'raw_end': q + len(s0) if q >= 0 else -1,
                 'vol': '', 'chunk': ''})
    added += 1
io.open(p, 'w', encoding='utf-8').writelines(json.dumps(r, ensure_ascii=False) + '\n' for r in rows)
print('rows', len(rows), 'added', added)
