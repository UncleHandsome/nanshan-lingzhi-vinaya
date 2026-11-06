# -*- coding: utf-8 -*-
"""只補篇1 缺失的 120 段序文記，不動篇2-10：
   zsecs 一開始就建立「序」節，篇界只認三十篇名；
   Z2S 映射沿用，故篇2-10 段數不變。
   同時把 篇1 的 am 與 bounds（卷首、篇01）整體 +120。
"""
import io, os, json, importlib.util

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\export_materials.py'
s = io.open(p, encoding='utf-8').read()

# --- zsecs: 保留序節、只認真篇名 ---
a = s.find('def zsecs():')
b = s.find('def zitems_for', a)
new = '''def zsecs():
    zj = []
    for k, sp, tt in load('資持記_細分', '資持記'):
        zj += list(zip(sp, tt))
    ZP = re.compile(r'釋([\\u4e00-\\u9fff]{2,6})篇')
    valid = [x['name'] for x in sections()]
    z = dict(name='序', items=[])
    zs = [z]
    for o, t in zj:
        m = ZP.search(o) or ZP.search(t)
        if m and any(v.startswith(m.group(1)) or m.group(1) in v for v in valid):
            z = dict(name=m.group(1), items=[])
            zs.append(z)
        z['items'].append((o, t))
    return zs


'''
s = s[:a] + new + s[b:]

# --- build_zi: 還原原本的 Z2S 映射 ---
a2 = s.find('def build_zi(secs, zs):')
b2 = s.find('def ', a2 + 10)
new2 = '''def build_zi(secs, zs):
    ZI = {i: [] for i in range(len(secs))}
    for i, sec in enumerate(zs):
        if i < len(Z2S):
            ZI[Z2S[i]] += sec['items']
    if len(ZI[13]) > 122:
        ZI[12] = ZI[12] + ZI[13][:122]
        ZI[13] = ZI[13][122:]
    if len(ZI[11]) > 90:
        ZI[12] = [ZI[11][-1]] + ZI[12]
        ZI[11] = ZI[11][:-1]
    ZI[29] = ZI[29][:28]
    return ZI


'''
s = s[:a2] + new2 + s[b2:]
io.open(p, 'w', encoding='utf-8').write(s)
print('zsecs/build_zi patched')

# --- 檢查段數 ---
spec = importlib.util.spec_from_file_location('ex', p)
ex = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ex)
ZI = ex.build_zi(ex.sections(), ex.zsecs())
print('counts', [len(ZI[i]) for i in range(12)])
zi0 = ZI[0]
off = next(i for i, (o, t) in enumerate(zi0) if '古科列名' in o)
print('古科 index', off, 'ZI0', len(zi0))

if off == 120:
    # hb_align：篇1 前補 120 個 0
    fp = os.path.join(B, 'AI語譯', '_work', 'hb_align.json')
    AM = json.load(io.open(fp, encoding='utf-8'))
    am0 = AM['0']
    if len(am0) == 329:
        AM['0'] = [0] * 120 + am0
        json.dump(AM, io.open(fp, 'w', encoding='utf-8'), ensure_ascii=False)
        print('hb_align 篇1 +120 zeros')
    # bounds：卷首、篇01 各 +120
    for nm in ['bounds_卷首.json', 'bounds_篇01.json']:
        bp = os.path.join(B, 'AI語譯', '_work', 'pian_bounds', nm)
        if not os.path.exists(bp):
            continue
        d = json.load(io.open(bp, encoding='utf-8-sig'))
        for x in d['bounds']:
            x['n'] = int(x['n']) + 120
        json.dump(d, io.open(bp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print(nm, '+120')
