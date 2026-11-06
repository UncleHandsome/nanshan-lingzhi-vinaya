# -*- coding: utf-8 -*-
"""把篇30 的記29-53（卷末校勘記）移出正文，另存 CSV"""
import io, os, csv, sys, importlib.util

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'

# 1) 先把資料取出（此時 build_zi 尚未截斷）
spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ex)
secs = ex.sections(); zs = ex.zsecs()
ZI = ex.build_zi(secs, zs)
Z = ZI[29]
tail = Z[28:]
out_csv = os.path.join(B, '合編材料', '篇30_卷末校勘記.csv')
with io.open(out_csv, 'w', encoding='utf-8-sig', newline='') as fh:
    w = csv.writer(fh)
    w.writerow(['原記序', '內容', '白話'])
    for i, (o, t) in enumerate(tail, start=29):
        w.writerow([i, o, t])
print('校勘記', len(tail), '段 →', out_csv)

# 2) 在 hebian_ju 與 export_materials 截斷篇30
for fname in ('hebian_ju.py', 'export_materials.py'):
    p = os.path.join(B, '_src', fname)
    s = io.open(p, encoding='utf-8').read()
    if '_ZI[29] = _ZI[29][:28]' in s or "ZI[29] = ZI[29][:28]" in s:
        print(fname, 'already truncated')
        continue
    if fname == 'hebian_ju.py':
        s = s.replace("""    if RE_SLICE and len(_ZI[11]) > 90:
        _ZI[12] = [_ZI[11][-1]] + _ZI[12]
        _ZI[11] = _ZI[11][:-1]""",
"""    if RE_SLICE and len(_ZI[11]) > 90:
        _ZI[12] = [_ZI[11][-1]] + _ZI[12]
        _ZI[11] = _ZI[11][:-1]
    # 篇30 記29-53 是卷末校勘記，不屬正文
    _ZI[29] = _ZI[29][:28]""")
    else:
        s = s.replace("""    if len(ZI[11]) > 90:
        ZI[12] = [ZI[11][-1]] + ZI[12]
        ZI[11] = ZI[11][:-1]""",
"""    if len(ZI[11]) > 90:
        ZI[12] = [ZI[11][-1]] + ZI[12]
        ZI[11] = ZI[11][:-1]
    ZI[29] = ZI[29][:28]""")
    io.open(p, 'w', encoding='utf-8').write(s)
    print(fname, 'truncated')
