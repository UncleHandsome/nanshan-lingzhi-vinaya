# -*- coding: utf-8 -*-
"""比對譯文段數與 AI語譯/_work/counts_before.json 是否一致。"""
import os, io, re, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
base = json.load(io.open(os.path.join(B, 'AI語譯', '_work', 'counts_before.json'), encoding='utf-8'))
bad = []
for rel, n in base.items():
    p = os.path.join(B, 'AI語譯', 'out', rel)
    if not os.path.exists(p):
        bad.append((rel, n, 'MISSING'))
        continue
    t = io.open(p, encoding='utf-8').read()
    k = len([x for x in re.split(r'\r?\n\r?\n', t) if x.strip()])
    if k != n:
        bad.append((rel, n, k))
print('files', len(base), 'changed-count', len(bad))
for x in bad[:40]:
    print('  ', x)
