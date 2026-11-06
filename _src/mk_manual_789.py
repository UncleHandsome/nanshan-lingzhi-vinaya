# -*- coding: utf-8 -*-
"""篇7-9 依使用者裁定寫入切點／搬移，並驗證 marker"""
import io, os, json, importlib.util

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
D = os.path.join(B, 'AI語譯', '_work', 'pian_manual')
M = {
    7: [
        {"n": 23, "base": 9, "markers": ["治法中，總列九種", "初訶責法。律明佛在舍衛"], "targets": [9, 10, 11]},
        {"n": 35, "base": 18, "markers": ["奪行中"], "targets": [18, 19]},
        {"n": 51, "base": 24, "markers": ["總簡中。以前後七法"], "targets": [24, 25]},
        {"n": 58, "base": 26, "markers": ["六不懺舉者"], "targets": [26, 27]},
        {"n": 77, "base": 33, "markers": ["正制中，初《四分》"], "targets": [33, 34]},
        {"n": 83, "base": 35, "markers": ["釋難中。僧事即食具"], "targets": [35, 36]},
        {"n": 86, "base": 36, "markers": ["明用與中，初科。云一無與者"], "targets": [36, 37]},
    ],
    8: [
        {"n": 22, "base": 6},
        {"n": 25, "base": 7, "markers": ["第二正加，點示中"], "targets": [7, 8]},
        {"n": 42, "base": 14, "markers": ["通簡中，初勸取宿德"], "targets": [14, 15]},
        {"n": 77, "base": 19, "markers": ["六出問，所以中"], "targets": [19, 20]},
        {"n": 80, "base": 20, "markers": ["初釋邊罪。從喻為名"], "targets": [20, 21]},
        {"n": 81, "base": 21, "markers": ["二明污尼，定淨穢中"], "targets": [21, 22]},
        {"n": 101, "base": 24, "markers": ["五黃門者。《疏》云：黃是中方之色"], "targets": [24, 25]},
        {"n": 104, "base": 25, "markers": ["三殺中。六七違恩"], "targets": [25, 26]},
        {"n": 106, "base": 27, "markers": ["非人中。且示鬼神"], "targets": [27, 28]},
        {"n": 107, "base": 28, "markers": ["畜生中。同取變化"], "targets": [28, 29]},
        {"n": 108, "base": 29, "markers": ["二形中，初示相"], "targets": [29, 30]},
        {"n": 112, "base": 31},
        {"n": 113, "base": 32},
        {"n": 146, "base": 55, "markers": ["白中，初科。布施戒者"], "targets": [55, 56]},
    ],
    9: [
        {"n": 15, "base": 5},
        {"n": 18, "base": 7},
        {"n": 24, "base": 11},
        {"n": 36, "base": 15},
        {"n": 37, "base": 16},
        {"n": 64, "base": 23},
    ],
}
for p, arr in M.items():
    fp = os.path.join(D, '篇%02d.json' % p)
    json.dump({"splits": arr}, io.open(fp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)
ZI = ex.build_zi(ex.sections(), ex.zsecs())
bad = 0
for p, arr in M.items():
    for e in arr:
        if 'markers' not in e:
            continue
        t = ZI[p - 1][e['n'] - 1][0]
        for mk in e['markers']:
            ok = mk in t
            if not ok:
                bad += 1
            print('篇%d 記%d %s %s' % (p, e['n'], 'OK ' if ok else 'MISS', mk))
print('missing:', bad)
