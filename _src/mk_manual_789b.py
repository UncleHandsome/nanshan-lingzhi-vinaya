# -*- coding: utf-8 -*-
"""依使用者 2026-11-07 清單，寫入篇7/8/9 切點（逐字驗證）"""
import io, os, json, importlib.util

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
D = os.path.join(B, 'AI語譯', '_work', 'pian_manual')

ADD = {
    7: [
        {"n": 20, "base": 7, "markers": ["斥濫中，初二句傷時不行"], "targets": [7, 8]},
        {"n": 98, "base": 42, "markers": ["四對處明用；威儀中"], "targets": [42, 43]},
        {"n": 107, "base": 44, "markers": ["五雜教授，能諫中"], "targets": [44, 45]},
    ],
    8: [
        {"n": 6, "base": 1, "markers": ["具緣中。舊記並科此為古五緣"], "targets": [1, 2]},
        {"n": 28, "base": 9, "markers": ["請和尚中。"], "targets": [9, 10]},
        {"n": 33, "base": 11, "markers": ["請二師法，標示中。"], "targets": [11, 12]},
        {"n": 35, "base": 13, "markers": ["料簡十師，弟子知中"], "targets": [13, 14]},
        {"n": 44, "base": 15, "markers": ["三發戒緣，敘意中"], "targets": [15, 16]},
        {"n": 75, "base": 18, "markers": ["五中，引緣。可解。"], "targets": [18, 19]},
        {"n": 122, "base": 34, "markers": ["父母中。《律》因身子"], "targets": [34, 35]},
        {"n": 128, "base": 39, "markers": ["五病中，初文。"], "targets": [39, 40]},
        {"n": 134, "base": 44, "markers": ["三中。不實，謂帶難"], "targets": [44, 45]},
        {"n": 142, "base": 52, "markers": ["十正問，初科中"], "targets": [52, 53]},
        {"n": 153, "base": 57, "markers": ["說相中，初科。"], "targets": [57, 58]},
        {"n": 168, "base": 61, "markers": ["捨戒中。總有四捨。"], "targets": [61, 62]},
    ],
    9: [
        {"n": 24, "base": 9, "markers": ["受法中。", "報恩中，"], "targets": [9, 10, 11]},
        {"n": 37, "base": 15, "markers": ["第四示緣中。"], "targets": [15, 16]},
    ],
}

for p, arr in ADD.items():
    fp = os.path.join(D, '篇%02d.json' % p)
    old = []
    if os.path.exists(fp):
        old = json.load(io.open(fp, encoding='utf-8-sig')).get('splits', [])
    keep = [e for e in old if int(e['n']) not in {int(x['n']) for x in arr}]
    json.dump({'splits': keep + arr}, io.open(fp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)
ZI = ex.build_zi(ex.sections(), ex.zsecs())
for p, arr in ADD.items():
    for e in arr:
        t = ZI[p - 1][e['n'] - 1][0]
        for mk in e['markers']:
            print('篇%d 記%3d %s %s' % (p, e['n'], 'OK ' if mk in t else 'MISS', mk))
