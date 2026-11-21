# -*- coding: utf-8 -*-
"""資持記 _終審 13 份材料對 raw 順序對齊。"""
import io
import os
import re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
T = os.path.join(B, '測試', '重譯', '資持記', '_終審')
R = os.path.join(B, 'TXT', '資持記')


def han(s):
    s = re.sub(r'■\s*[^\n（]*（原文）', '', s)
    s = re.sub(r'^(?:【[^】]+】)+', '', s.strip())
    return ''.join(re.findall(r'[\u4e00-\u9fff]', s))


raw = ''
maps = []
for f in sorted(os.listdir(R)):
    if not f.endswith('.txt'):
        continue
    t = io.open(os.path.join(R, f), encoding='utf-8').read()
    start = len(raw)
    raw += t
    maps.append((start, len(raw), f))
h = ''
mp = []
for i, c in enumerate(raw):
    if '\u4e00' <= c <= '\u9fff':
        h += c
        mp.append(i)
items = []
for f in sorted(os.listdir(T)):
    if not f.endswith('.md'):
        continue
    md = io.open(os.path.join(T, f), encoding='utf-8').read()
    i = md.rfind('【原文】')
    j = md.rfind('【待審譯文】')
    if i < 0 or j < 0:
        continue
    s = han(md[i + 4:j])
    q = -1
    for n in (20, 12, 8, 6):
        q = h.find(s[:n]) if len(s) >= n else -1
        if q >= 0:
            break
    items.append((q if q >= 0 else 10**9, f[:-3], s, q))
items.sort()
lines = ['# 資持記終審材料順序對齊', '', '| key | raw 位置 | 檔案 | 長度 |', '|:--|--:|:--|--:|']
for q, k, s, real in items:
    chunk = ''
    for a, b, fn in maps:
        if real >= a and real < b:
            chunk = fn
            break
    lines.append('| %s | %s | %s | %d |' % (k, real if real >= 0 else '找不到', chunk or '—', len(s)))
fp = os.path.join(B, '重作材料_長段', '資持記_終審對齊.md')
io.open(fp, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print(fp)
