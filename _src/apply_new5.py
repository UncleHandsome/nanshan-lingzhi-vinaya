# -*- coding: utf-8 -*-
"""套用 new5（篇13、篇14）對應表"""
import io, os, re, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
SRC = os.path.join(B, '合編材料', 'new5.txt')
ours = {13: 135, 14: 1087}

t = io.open(SRC, encoding='utf-8').read()
parts = re.split(r'###\s*【工作表\s*(\d+)】[^\n]*篇\s*(\d+)', t)
rows_by = {}
for i in range(1, len(parts), 3):
    pian = int(parts[i + 1])
    body = parts[i + 2] if i + 2 < len(parts) else ''
    rows = []
    for line in body.split('\n'):
        if not line.strip().startswith('|'):
            continue
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) < 3:
            continue
        m = re.match(r'^\*{0,2}(\d+)', cells[0])
        if not m:
            continue
        c = int(m.group(1))
        nums = [int(x) for x in re.findall(r'\d+', cells[2])]
        if not nums:
            continue
        a, b = nums[0], (nums[1] if len(nums) > 1 else nums[0])
        if b < a:
            a, b = b, a
        rows.append((a, b, c))
    if rows:
        rows_by.setdefault(pian, []).extend(rows)

main = json.load(io.open(os.path.join(B, 'AI語譯', '_work', 'hb_align.json'), encoding='utf-8'))
applied = []
for p, rs in sorted(rows_by.items()):
    rs.sort()
    mx = max(b for a, b, c in rs)
    n = ours.get(p)
    print('篇%-3d 列%-4d 記號最大%-5d 現有%-5s %s' % (p, len(rs), mx, n, '✓' if mx == n else '✗'))
    if mx != n:
        continue
    arr = [None] * (mx + 1)
    for a, b, c in rs:
        for z in range(a, min(b, mx) + 1):
            arr[z] = c
    last = 1
    for i in range(1, mx + 1):
        arr[i] = last if arr[i] is None else arr[i]
        last = arr[i]
    main[str(p - 1)] = arr[1:]
    applied.append(p)
json.dump(main, io.open(os.path.join(B, 'AI語譯', '_work', 'hb_align.json'), 'w', encoding='utf-8'), ensure_ascii=False)
print('套用', applied)
