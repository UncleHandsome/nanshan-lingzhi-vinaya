# -*- coding: utf-8 -*-
"""寫入人工切點表（篇1、篇3、篇5 局部）"""
import io, os, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
D = os.path.join(B, 'AI語譯', '_work', 'pian_manual')
os.makedirs(D, exist_ok=True)
M = {
    1: [
        {"n": 253, "base": 3, "markers": ["戒體中，初科為二"], "targets": [3, 4]},
        {"n": 258, "base": 4, "markers": ["戒行中三"], "targets": [4, 5]},
        {"n": 261, "base": 5, "markers": ["戒相中二"], "targets": [5, 6]},
        {"n": 278, "base": 10, "markers": ["大乘經，《華嚴》"], "targets": [10, 11]},
        {"n": 287, "base": 11, "markers": ["大乘論，《智論》"], "targets": [11, 12]},
        {"n": 311, "base": 14, "markers": ["違戒中。還約者"], "targets": [14, 15]},
        {"n": 324, "base": 15, "markers": ["問中，彼論前云"], "targets": [15, 16]},
    ],
    3: [
        {"n": 7, "base": 2, "markers": ["《十誦》文見五十四"], "targets": [2, 3]},
    ],
    5: [
        {"n": 39, "base": 10, "markers": ["第二明事有三"], "targets": [10, 11]},
        {"n": 74, "base": 30, "markers": ["通塞中，單白分二"], "targets": [30, 31]},
    ],
}
for p, arr in M.items():
    fp = os.path.join(D, '篇%02d.json' % p)
    json.dump({"splits": arr}, io.open(fp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(fp, len(arr))
