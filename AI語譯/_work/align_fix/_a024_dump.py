#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dump hebian HTML blocks (鈔/記) for 僧像致敬篇 (section 22) into a readable text file."""
import re, html, json, io, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
HB = os.path.join(ROOT, 'docs', 'hebian', '卷下之三.html')

t = open(HB, encoding='utf-8').read()
# split on pair divs
parts = re.split(r'<div class="pair" id="s(\d+)">', t)
# parts[0] = prefix; then triples (id, body, ...)
blocks = []
for i in range(1, len(parts), 2):
    sid = parts[i]
    body = parts[i+1]
    m = re.match(r'\s*<div class="(o2?)">(.*?)</div>', body, re.S)
    if not m:
        continue
    cls, txt = m.group(1), m.group(2)
    txt = re.sub(r'<[^>]+>', '', txt)
    txt = html.unescape(txt).strip()
    kind = 'C' if cls == 'o' else 'J'
    blocks.append((int(sid), kind, txt))

# locate section 22 in 鈔 order: find block whose text starts with 【鈔】22
start = end = None
for idx, (sid, k, txt) in enumerate(blocks):
    if k == 'C' and txt.startswith('【鈔】22 僧像致敬'):
        start = idx
    if start is not None and k == 'C' and txt.startswith('【鈔】23 訃請設則'):
        end = idx
        break
if end is None:
    end = len(blocks)
print('blocks', len(blocks), 'start', start, 'end', end)

sub = blocks[start:end]
out = []
for sid, k, txt in sub:
    out.append(('C' if k == 'C' else 'J', txt))
json.dump(out, open(os.path.join(HERE, '_a024_hb.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

with open(os.path.join(HERE, '_a024_hb.txt'), 'w', encoding='utf-8') as f:
    ci = ji = 0
    for k, txt in out:
        if k == 'C':
            f.write(f'\n######## C{ci} (s{sid}) ########\n{txt}\n')
            ci += 1
        else:
            f.write(f'\n@@@@@@@@ J{ji} ########\n{txt}\n')
            ji += 1
print('C', ci, 'J', ji)
