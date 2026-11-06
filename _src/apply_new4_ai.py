# -*- coding: utf-8 -*-
"""套用 new4（篇13-15）對應表"""
import io, os, re, json, glob

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
D = os.path.join(B, 'AI語譯', '_work', 'new4_ai')
ours = {13: 135, 14: 1087, 15: 241}
main = json.load(io.open(os.path.join(B, 'AI語譯', '_work', 'hb_align.json'), encoding='utf-8'))
applied = []
for f in sorted(glob.glob(os.path.join(D, 'out_*.json'))):
    m = re.search(r'篇(\d+)', os.path.basename(f))
    if not m:
        continue
    p = int(m.group(1))
    d = json.load(io.open(f, encoding='utf-8-sig'))
    rs = d.get('rows', [])
    if not rs:
        print('篇', p, '無資料')
        continue
    mx = max(r['ji_to'] for r in rs)
    n = ours.get(p)
    print('篇%-3d 列%-4d 記號最大%-5d 現有%-5s %s' % (p, len(rs), mx, n, '✓' if mx == n else '✗'))
    if mx != n:
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
