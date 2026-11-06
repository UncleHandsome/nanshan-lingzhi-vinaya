# -*- coding: utf-8 -*-
"""收集 new3 AI 整理結果並比對記段數"""
import io, os, glob, json, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
D = os.path.join(B, 'AI語譯', '_work', 'new3_ai')
ours = {19: 42, 20: 35, 21: 61, 22: 92, 23: 57, 24: 88, 25: 16,
        26: 41, 27: 47, 28: 93, 29: 55, 30: 53}
main = json.load(io.open(os.path.join(B, 'AI語譯', '_work', 'hb_align.json'), encoding='utf-8'))
rows_all = {}
for f in sorted(glob.glob(os.path.join(D, 'out_*.json'))):
    try:
        d = json.load(io.open(f, encoding='utf-8-sig'))
    except Exception:
        continue
    m = re.search(r'篇(\d+)', os.path.basename(f))
    if not m:
        continue
    p = int(m.group(1))
    rows_all[p] = d.get('rows', [])
print('篇  列數  AI記號 現有  可用')
applied = []
for p in sorted(ours):
    rs = rows_all.get(p, [])
    if not rs:
        print('%-3d %4d %6s %5d  ✗（未產出）' % (p, 0, '-', ours[p]))
        continue
    mx = max(r['ji_to'] for r in rs)
    ok = (mx == ours[p])
    print('%-3d %4d %6d %5d  %s' % (p, len(rs), mx, ours[p], '✓' if ok else '✗'))
    if not ok:
        continue
    arr = [None] * (mx + 1)
    for r in rs:
        for z in range(r['ji_from'], min(r['ji_to'], mx) + 1):
            arr[z] = r['chao']
    last = 0
    for i in range(1, mx + 1):
        arr[i] = last if arr[i] is None else arr[i]
        last = arr[i]
    main[str(p - 1)] = arr[1:]
    applied.append(p)
json.dump(main, io.open(os.path.join(B, 'AI語譯', '_work', 'hb_align.json'), 'w', encoding='utf-8'), ensure_ascii=False)
print('套用', applied)
