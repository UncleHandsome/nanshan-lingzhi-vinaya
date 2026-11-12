# -*- coding: utf-8 -*-
import os, re, json, collections, sys
ROOT = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
RD = os.path.join(ROOT, 'batch_qwen', 'r2')
HDR = re.compile(r'^\s*(#{1,6})?\s*[【\[]?\s*(\d{4})-(\d{4})\s*[】\]]?')
cont = 0
files = []
for n in range(1181, 1331):
    p = os.path.join(RD, 'resp_%d.txt' % n)
    if not os.path.exists(p):
        files.append((n, None)); continue
    s = open(p, encoding='utf-8').read()
    hs = HDR.findall(s) if False else [m for m in HDR.finditer(s)]
    # count only lines starting with header-like markers
    lines = s.split('\n')
    hits = [l for l in lines if HDR.match(l)]
    files.append((n, len(hits)))
    cont += len(hits)
print('headers total', cont)
print('no-header files:', [n for n, c in files if c == 0])
print('sample counts:', files[:12])
print('avg', cont / max(1, len([c for n, c in files if c is not None])))
