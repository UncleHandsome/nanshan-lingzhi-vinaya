# -*- coding: utf-8 -*-
"""把資持記分節依名稱對到篇（含十三僧殘），恢復篇11-30 記段數"""
import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\export_materials.py'
s = io.open(p, encoding='utf-8').read()

# zsecs：接受十三僧殘
s = s.replace("if m and any(v.startswith(m.group(1)) or m.group(1) in v for v in valid):",
              "if m and (m.group(1) == '十三僧殘' or any(v.startswith(m.group(1)) or m.group(1) in v for v in valid)):")

# build_zi：以名稱對篇
a = s.find('def build_zi(secs, zs):')
b = s.find('def ', a + 10)
new = '''NAME2P = {
    '序': 0, '標宗': 0, '集僧': 1, '足數': 2, '受欲': 3, '羯磨': 4, '結界': 5,
    '僧網': 6, '受戒': 7, '師資': 8, '說戒': 9, '安居': 10, '自恣': 11,
    '篇聚': 12, '釋相': 13, '十三僧殘': 13, '持犯': 14, '懺六聚法': 15, '二衣': 16,
    '四藥': 17, '鉢器': 18, '對施': 19, '頭陀': 20, '僧像': 21, '訃請': 22,
    '導俗': 23, '主客': 24, '瞻病': 25, '諸雜': 26, '沙彌': 27, '尼眾': 28, '諸部': 29,
}


def build_zi(secs, zs):
    ZI = {i: [] for i in range(len(secs))}
    for z in zs:
        idx = NAME2P.get(z['name'])
        if idx is None:
            continue
        ZI[idx] += z['items']
    if len(ZI[13]) > 122:
        ZI[12] = ZI[12] + ZI[13][:122]
        ZI[13] = ZI[13][122:]
    if len(ZI[11]) > 90:
        ZI[12] = [ZI[11][-1]] + ZI[12]
        ZI[11] = ZI[11][:-1]
    ZI[29] = ZI[29][:28]
    return ZI


'''
s = s[:a] + new + s[b:]
io.open(p, 'w', encoding='utf-8').write(s)
print('name mapping v2')

import importlib.util
spec = importlib.util.spec_from_file_location('ex', p)
ex = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ex)
ZI = ex.build_zi(ex.sections(), ex.zsecs())
print([len(ZI[i]) for i in range(30)])
