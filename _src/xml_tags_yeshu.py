# -*- coding: utf-8 -*-
"""從 CBETA XML 取【疏】(orig)/【記】(commentary) 標記，對應到分卷段落"""
import io, os, re, json, bisect
import xml.etree.ElementTree as ET

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
S = os.path.join(B, 'TXT_分卷', '03_業疏')
XML = os.path.join(B, '_xml', 'X41n0728.xml')
NS = {'t': 'http://www.tei-c.org/ns/1.0', 'cb': 'http://www.cbeta.org/ns/1.0'}
han = lambda s: ''.join(re.findall(r'[\u4e00-\u9fff]', s))

tree = ET.parse(XML)
root = tree.getroot()

# 逐個 div 取 type 與其 <p> 文字
blocks = []      # (type, text)
seen = set()
for div in root.iter():
    if not div.tag.endswith('div'):
        continue
    typ = div.get('type')
    if typ not in ('orig', 'commentary'):
        continue
    for p in div.iter('{http://www.tei-c.org/ns/1.0}p'):
        if id(p) in seen:
            continue
        seen.add(id(p))
        txt = ''.join(p.itertext())
        h = han(txt)
        if h:
            blocks.append((typ, txt, h))
print('XML 段', len(blocks), 'orig', sum(1 for b in blocks if b[0] == 'orig'),
      'commentary', sum(1 for b in blocks if b[0] == 'commentary'))

X = ''.join(b[2] for b in blocks)
starts = []
acc = 0
for b in blocks:
    starts.append(acc)
    acc += len(b[2])
print('XML 字數', len(X))

# 分卷段落
sp_all = []
for f in sorted(os.listdir(S), key=lambda x: (0 if x.startswith('00_') else 1, x)):
    if not f.endswith('.txt'):
        continue
    sp = [x.strip() for x in io.open(os.path.join(S, f), encoding='utf-8').read().split('\n')[5:] if x.strip()]
    sp_all += [(f[:-4], x) for x in sp]

tags = []
miss = 0
for key, x in sp_all:
    h = han(x)
    if not h:
        tags.append('')
        continue
    probe = h[:14] if len(h) >= 14 else h
    pos = X.find(probe)
    if pos < 0:
        probe = h[:8]
        pos = X.find(probe)
    if pos < 0:
        tags.append('')
        miss += 1
        continue
    i = bisect.bisect_right(starts, pos) - 1
    typ = blocks[i][0]
    tags.append('【疏】' if typ == 'orig' else '【記】' if typ == 'commentary' else '')
print('對應成功', len(tags) - miss, '/', len(tags), '失敗', miss)
from collections import Counter
print(Counter(t for t in tags if t))

json.dump(tags, io.open(os.path.join(B, 'AI語譯', '_work', 'yeshu_tags.json'), 'w', encoding='utf-8'), ensure_ascii=False)
