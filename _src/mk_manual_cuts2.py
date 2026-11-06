# -*- coding: utf-8 -*-
"""依使用者裁定寫入 11 處手動切點／搬移"""
import io, os, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
D = os.path.join(B, 'AI語譯', '_work', 'pian_manual')
os.makedirs(D, exist_ok=True)
M = {
    2: [
        {"n": 27, "base": 4, "markers": ["標示中。制意開緣", "作法三者，場及大小"], "targets": [4, 5, 6]},
        {"n": 35, "base": 10, "markers": ["不可分別中分二"], "targets": [10, 11]},
        {"n": 45, "base": 14, "markers": ["論體中"], "targets": [14, 15]},
    ],
    3: [
        {"n": 13, "base": 5, "markers": ["神足中", "隱沒中", "離見聞中"], "targets": [5, 6, 7, 8]},
        {"n": 14, "base": 8},
        {"n": 52, "base": 34},
        {"n": 53, "base": 34},
    ],
    4: [
        {"n": 20, "base": 13, "markers": ["轉欲，敘緣中"], "targets": [13, 14]},
        {"n": 30, "base": 19, "markers": ["次決通中"], "targets": [19, 20]},
        {"n": 50, "base": 31},
    ],
    5: [
        {"n": 52, "base": 17, "markers": ["第四。人非中", "第五。人非中"], "targets": [17, 18, 19]},
        {"n": 53, "base": 19, "markers": ["第六。法非中"], "targets": [19, 20]},
        {"n": 54, "base": 20, "markers": ["第七。人非中", "第八。人非中"], "targets": [20, 21, 22]},
    ],
}
for p, arr in M.items():
    fp = os.path.join(D, '篇%02d.json' % p)
    old = []
    if os.path.exists(fp):
        old = json.load(io.open(fp, encoding='utf-8-sig')).get('splits', [])
    # 保留篇1 既有；其他覆寫
    json.dump({"splits": arr}, io.open(fp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(fp, len(arr))

# 驗證 markers 是否存在
import importlib.util
spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)
ZI = ex.build_zi(ex.sections(), ex.zsecs())
for p, arr in M.items():
    for e in arr:
        if 'markers' not in e:
            print('篇%d 搬移 記%d → 鈔%d' % (p, e['n'], e['base']))
            continue
        t = ZI[p - 1][e['n'] - 1][0]
        for mk in e['markers']:
            print('篇%d 記%d marker %s : %s' % (p, e['n'], 'OK' if mk in t else 'MISSING', mk))
