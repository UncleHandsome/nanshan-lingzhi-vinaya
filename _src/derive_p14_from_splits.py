# -*- coding: utf-8 -*-
"""由 AI 切點反推 篇14 的鈔界，使切點全部通過驗證且順序單調"""
import io, os, json, importlib.util

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)
ZI = ex.build_zi(ex.sections(), ex.zsecs())[13]
N = len(ZI)

SP = json.load(io.open(os.path.join(B, 'AI語譯', '_work', 'pian_split_out', 'split_篇14.json'), encoding='utf-8-sig'))['splits']
smap = {int(e['n']): e for e in SP}

cur = 1
cmap = {}
out_splits = []
for n in range(1, N + 1):
    e = smap.get(n)
    if e and 'markers' in e:
        tg = sorted(int(x) for x in e['targets'])
        # 第一片必須落在目前位置
        tg = [cur] + [x for x in tg if x > cur]
        tg = sorted(set(tg))
        # 讓 targets 連續（建置器要求）
        tg = list(range(cur, cur + len(tg)))
        # 檢查 marker 存在
        o = ZI[n - 1][0]
        if all(m in o for m in e['markers']) and len(tg) == len(e['markers']) + 1:
            cmap[n] = cur
            out_splits.append({'n': n, 'base': cur, 'markers': e['markers'], 'targets': tg})
            cur = tg[-1]
            continue
    cmap[n] = cur

# 由 cmap 產 bounds：每個 c 的第一個 n
bounds = {}
for n in range(1, N + 1):
    c = cmap[n]
    bounds.setdefault(c, n)
bs = [{'c': c, 'n': bounds[c]} for c in sorted(bounds)]

json.dump({'bounds': bs}, io.open(os.path.join(B, 'AI語譯', '_work', 'pian_bounds', 'bounds_篇14.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump({'splits': out_splits}, io.open(os.path.join(B, 'AI語譯', '_work', 'pian_split_out', 'split_篇14.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('bounds', len(bs), 'c max', bs[-1]['c'], 'splits', len(out_splits), 'cur end', cur)
