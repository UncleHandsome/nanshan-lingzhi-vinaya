# -*- coding: utf-8 -*-
"""把 AI 整理的 new2 表格轉成對應陣列，檢查是否可用"""
import io, os, json, sys, importlib.util

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ex)
ZS = ex.zsecs()
SECS = ex.sections()
ours = {11: 128, 12: 96, 13: 135, 14: 1087, 15: 241, 16: 148, 17: 273, 18: 115, 19: 42, 20: 35}

rows = json.load(io.open(os.path.join(B, 'AI語譯', '_work', 'new2_ai_all.json'), encoding='utf-8'))
main = json.load(io.open(os.path.join(B, 'AI語譯', '_work', 'hb_align.json'), encoding='utf-8'))
applied, report = [], []
for p, rs in sorted(rows.items(), key=lambda x: int(x[0])):
    p = int(p)
    mx = max((r.get('ji_to') or 0) for r in rs)
    n = ours.get(p)
    ok = (mx == n)
    report.append((p, len(rs), mx, n, ok))
    if not ok:
        continue
    arr = [None] * (mx + 1)
    for r in rs:
        a, b, c = int(r['ji_from']), int(r['ji_to']), int(r['chao'])
        for z in range(a, min(b, mx) + 1):
            arr[z] = c
    last = 0
    for i in range(1, mx + 1):
        if arr[i] is None:
            arr[i] = last
        else:
            last = arr[i]
    main[str(p - 1)] = arr[1:]
    applied.append(p)
json.dump(main, io.open(os.path.join(B, 'AI語譯', '_work', 'hb_align.json'), 'w', encoding='utf-8'), ensure_ascii=False)
print('篇  列數  記號最大  現有  可用')
for p, k, mx, n, ok in report:
    print('%-3d %5d %8d %6s  %s' % (p, k, mx, n, '✓' if ok else '✗'))
print('套用', applied)
