import io, importlib.util, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\export_materials.py'
s = io.open(p, encoding='utf-8').read()

start = s.find('def build_zi(secs, zs):')
end = s.find('def ', start + 10)
assert start > 0 and end > start
new = '''def build_zi(secs, zs):
    ZI = {i: [] for i in range(len(secs))}
    for z in zs:
        nm = z['name']
        idx = None
        if nm == '序':
            idx = 0
        else:
            for i, sec in enumerate(secs):
                sn = sec['name']
                if sn == nm or sn.startswith(nm) or nm.startswith(sn):
                    idx = i
                    break
        if idx is None:
            continue
        ZI[idx] += z['items']
    # 與 hebian_ju 相同的重切
    if len(ZI[13]) > 122:
        ZI[12] = ZI[12] + ZI[13][:122]
        ZI[13] = ZI[13][122:]
    if len(ZI[11]) > 90:
        ZI[12] = [ZI[11][-1]] + ZI[12]
        ZI[11] = ZI[11][:-1]
    ZI[29] = ZI[29][:28]
    return ZI


'''
s = s[:start] + new + s[end:]
io.open(p, 'w', encoding='utf-8').write(s)
print('build_zi by name')

spec = importlib.util.spec_from_file_location('ex', p)
ex = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ex)
ZI = ex.build_zi(ex.sections(), ex.zsecs())
print('各篇段數:', [len(ZI[i]) for i in range(10)])
print('ZI0 首段:', ZI[0][0][0][:40])
print('ZI0 含古科?', any('古科列名' in o for o, t in ZI[0][:400]))
