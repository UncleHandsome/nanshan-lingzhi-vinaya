# -*- coding: utf-8 -*-
"""重新解析 new.txt（篇1-10）並覆蓋 hb_align"""
import io, os, re, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
SRC = os.path.join(B, '合編材料', 'new.txt')
t = io.open(SRC, encoding='utf-8').read()

# 以「【工作表 N】篇NN_名」為界
parts = re.split(r'【工作表\s*(\d+)】\s*篇\s*(\d+)_', t)
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

print('解析到篇：', sorted(rows_by))
for p in sorted(rows_by):
    mx = max(b for a, b, c in rows_by[p])
    print('  篇%-3d 列%-3d 記號最大%-4d 首列%s' % (p, len(rows_by[p]), mx, rows_by[p][0]))
json.dump({str(k): v for k, v in rows_by.items()},
          io.open(os.path.join(B, 'AI語譯', '_work', 'new_txt_rows.json'), 'w', encoding='utf-8'),
          ensure_ascii=False)
