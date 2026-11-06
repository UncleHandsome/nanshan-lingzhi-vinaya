# -*- coding: utf-8 -*-
"""套用重新解析的 new.txt（段數相符者）"""
import io, os, json, sys, importlib.util

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ex)
secs = ex.sections(); zs = ex.zsecs()
ZI = ex.build_zi(secs, zs)
rows = json.load(io.open(os.path.join(B, 'AI語譯', '_work', 'new_txt_rows.json'), encoding='utf-8'))
main = json.load(io.open(os.path.join(B, 'AI語譯', '_work', 'hb_align.json'), encoding='utf-8'))
applied = []
for p, rs in sorted(((int(k), v) for k, v in rows.items())):
    if p > 10:
        continue
    n = len(ZI.get(p - 1, []))
    mx = max(b for a, b, c in rs)
    if mx != n:
        print('篇%-3d 記號最大%-4d 現有%-4d ✗' % (p, mx, n))
        continue
    # 只保留單調遞增的列（濾掉表格尾端混入的其他區塊）
    rs = sorted(rs)
    clean, last_c, prev_b = [], 0, 0
    for a, b, c in rs:
        if c < last_c or a <= prev_b:
            continue
        clean.append((a, b, c))
        last_c, prev_b = c, max(prev_b, b)
    rs = clean
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
