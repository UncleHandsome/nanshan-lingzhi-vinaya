# -*- coding: utf-8 -*-
"""切分 new4.txt 並用 AI 抽取篇13-15 對應表"""
import io, os, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
SRC = os.path.join(B, '合編材料', 'new4.txt')
OUT = os.path.join(B, 'AI語譯', '_work', 'new4_sec')
os.makedirs(OUT, exist_ok=True)
for f in os.listdir(OUT):
    os.remove(os.path.join(OUT, f))
lines = io.open(SRC, encoding='utf-8').read().split('\n')
marks = []
for i, l in enumerate(lines):
    m = re.match(r'^#+\s*【工作表\s*(\d+)】\s*[:：]\s*篇\s*(\d+)', l)
    if m:
        marks.append((i, int(m.group(2))))
for k, (i, p) in enumerate(marks):
    end = marks[k + 1][0] if k + 1 < len(marks) else len(lines)
    seg = '\n'.join(lines[i:end])
    io.open(os.path.join(OUT, '篇%02d.txt' % p), 'w', encoding='utf-8').write(seg)
    print('篇%02d 行 %d-%d (%d 字)' % (p, i + 1, end, len(seg)))
