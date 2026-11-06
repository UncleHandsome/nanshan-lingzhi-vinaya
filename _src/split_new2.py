# -*- coding: utf-8 -*-
"""把 new2.txt 依篇切成小檔（寬鬆比對標題）"""
import io, os, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
SRC = os.path.join(B, '合編材料', 'new2.txt')
OUT = os.path.join(B, 'AI語譯', '_work', 'new2_sec')
os.makedirs(OUT, exist_ok=True)
for f in os.listdir(OUT):
    os.remove(os.path.join(OUT, f))

lines = io.open(SRC, encoding='utf-8').read().split('\n')
marks = []
for i, l in enumerate(lines):
    if l.lstrip().startswith('#'):
        m = re.search(r'工作表\s*(\d+)', l)
        p = re.search(r'篇\s*(\d+)\s*_?', l)
        if m and p and 11 <= int(p.group(1)) <= 20:
            marks.append((i, int(p.group(1))))
# 去重（同篇多個標題取第一個）
seen = {}
for i, p in marks:
    seen.setdefault(p, i)
marks = sorted((i, p) for p, i in seen.items())
for k, (i, p) in enumerate(marks):
    end = marks[k + 1][0] if k + 1 < len(marks) else min(len(lines), i + 500)
    seg = '\n'.join(lines[i:end])
    io.open(os.path.join(OUT, '篇%02d.txt' % p), 'w', encoding='utf-8').write(seg)
    print('篇%02d 行 %d-%d (%d 字)' % (p, i + 1, end, len(seg)))
