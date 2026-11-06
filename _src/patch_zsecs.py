# -*- coding: utf-8 -*-
"""修正 zsecs 誤判篇界：只認《行事鈔》三十篇名，並保留篇界前的序文記段"""
import io, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\export_materials.py'
s = io.open(p, encoding='utf-8').read()

old = """    ZP = re.compile(r'釋([\\u4e00-\\u9fff]{2,6})篇')
    zs, z = [], None
    for o, t in zj:
        m = ZP.search(o) or ZP.search(t)
        if m:
            z = dict(name=m.group(1), items=[])
            zs.append(z)
        if z is not None:
            z['items'].append((o, t))
    return zs"""
new = """    ZP = re.compile(r'釋([\\u4e00-\\u9fff]{2,6})篇')
    # 只把《行事鈔》真正篇名當篇界，避免「釋云為顯諸篇」這類句子誤切
    valid = set()
    for bb, sp, tt in load('01_行事鈔', '行事鈔'):
        for t in sp:
            m2 = PATS.match(t.strip())
            if m2:
                valid.add(m2.group(1))
    zs, z = [], None
    for o, t in zj:
        if z is None:
            z = dict(name='序', items=[])
            zs.append(z)
        m = ZP.search(o) or ZP.search(t)
        if m and m.group(1) in valid:
            z = dict(name=m.group(1), items=[])
            zs.append(z)
        z['items'].append((o, t))
    return zs"""
assert old in s
s = s.replace(old, new)

old2 = """def build_zi(secs, zs):
    ZI = {i: [] for i in range(len(secs))}
    for i, sec in enumerate(zs):
        if i < len(Z2S):
            ZI[Z2S[i]] += sec['items']"""
new2 = """def build_zi(secs, zs):
    ZI = {i: [] for i in range(len(secs))}
    zmap = Z2S
    if zs and zs[0]['name'] == '序' and len(zs) == len(Z2S) + 1:
        zmap = [0] + Z2S            # 多了開頭的「序」節，映射整體後移
    for i, sec in enumerate(zs):
        if i < len(zmap):
            ZI[zmap[i]] += sec['items']"""
assert old2 in s
s = s.replace(old2, new2)
io.open(p, 'w', encoding='utf-8').write(s)
print('zsecs fixed + build_zi mapping shift')

# 檢查結果
import importlib.util
spec = importlib.util.spec_from_file_location('ex', p)
ex = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ex)
ZI = ex.build_zi(ex.sections(), ex.zsecs())
print('ZI[0] 段數', len(ZI[0]))
print('前 3 段:', ZI[0][0][0][:30], '|', ZI[0][1][0][:30], '|', ZI[0][2][0][:30])
