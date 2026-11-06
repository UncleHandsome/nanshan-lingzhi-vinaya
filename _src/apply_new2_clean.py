# -*- coding: utf-8 -*-
"""由 clean CSV 重建對應表並套用到 hb_align（只套段數相符者）"""
import io, os, re, csv, json, sys, importlib.util

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ex)
ZS = ex.zsecs()
SECS = ex.sections()
ours = {i + 1: len(ex.zitems_for(i, ZS)) for i in range(len(SECS))}
NAME2N = {s['name']: i + 1 for i, s in enumerate(SECS)}

rows = list(csv.DictReader(io.open(os.path.join(B, '合編材料', 'new2_clean.csv'), encoding='utf-8-sig')))
by = {}
for r in rows:
    pian = r['pian']
    n = NAME2N.get(pian)
    if not n:
        continue
    c0 = r['chao']
    if c0 in ('篇前', '開卷', '篇題'):
        c = 0
    else:
        m = re.match(r'(\d+)', c0)
        if not m:
            continue
        c = int(m.group(1))
    refs = re.sub(r'Sheet\s*\d+', '', r['refs'])
    nums = [int(x) for x in re.findall(r'\d+', refs)]
    if not nums:
        continue
    a, b = nums[0], (nums[1] if len(nums) > 1 else nums[0])
    if b < a:
        a, b = b, a
    by.setdefault(n, []).append((a, b, c))

main = json.load(io.open(os.path.join(B, 'AI語譯', '_work', 'hb_align.json'), encoding='utf-8'))
applied = []
for n, rs in by.items():
    rs.sort()
    mx = max(b for a, b, c in rs)
    if mx != ours.get(n):
        print('篇%-3d 記號最大 %-4d 現有 %-4d 跳過' % (n, mx, ours.get(n)))
        continue
    arr = [None] * (mx + 1)
    for a, b, c in rs:
        for z in range(a, min(b, mx) + 1):
            arr[z] = c
    last = 0
    for i in range(1, mx + 1):
        if arr[i] is None:
            arr[i] = last
        else:
            last = arr[i]
    main[str(n - 1)] = arr[1:]
    applied.append(n)
json.dump(main, io.open(os.path.join(B, 'AI語譯', '_work', 'hb_align.json'), 'w', encoding='utf-8'), ensure_ascii=False)
print('套用', applied)
