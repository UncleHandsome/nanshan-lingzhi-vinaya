# -*- coding: utf-8 -*-
"""重新解析 new.txt：以【工作表 N】切段，篇號取標題中的 篇NN"""
import io, os, re, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
t = io.open(os.path.join(B, '合編材料', 'new.txt'), encoding='utf-8').read()
chunks = re.split(r'【工作表\s*\d+】', t)
rows_by = {}
for ch in chunks[1:]:
    m = re.match(r'\s*篇\s*(\d+)', ch)
    if not m:
        continue
    p = int(m.group(1))
    rows = []
    for line in ch.split('\n'):
        if not line.strip().startswith('|'):
            continue
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) < 3:
            continue
        c0 = cells[0].replace('*', '').strip()
        if any(k in c0 for k in ('篇前', '開卷', '篇題')):
            c = 0
        else:
            mm = re.match(r'^(\d+)', c0)
            if not mm:
                continue
            c = int(mm.group(1))
        nums = [int(x) for x in re.findall(r'\d+', cells[2])]
        if not nums:
            continue
        a, b = nums[0], (nums[1] if len(nums) > 1 else nums[0])
        if b < a:
            a, b = b, a
        rows.append((a, b, c))
    if rows:
        rows_by.setdefault(p, []).extend(rows)
print('篇：', sorted(rows_by))
for p in sorted(rows_by):
    mx = max(b for a, b, c in rows_by[p])
    print('  篇%-3d 列%-3d 記號最大%-4d' % (p, len(rows_by[p]), mx))
json.dump({str(k): v for k, v in rows_by.items()},
          io.open(os.path.join(B, 'AI語譯', '_work', 'new_txt_rows.json'), 'w', encoding='utf-8'),
          ensure_ascii=False)
