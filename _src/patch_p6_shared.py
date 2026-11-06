import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\mk_p6_relational.py'
s = io.open(p, encoding='utf-8').read()
old = """    ks = by_c.get(cno, [])
    rows.append((cno, re.sub(r'\\s+', '', it[0])[:34],
                 ('記%d–%d' % (ks[0], ks[-1])) if ks else '（無記）'))"""
new = """    ks = by_c.get(cno, [])
    SHARED = {22: 53, 24: 55, 27: 58, 28: 58, 34: 67, 36: 68, 39: 74, 41: 76, 46: 83, 50: 88, 51: 88}
    if ks:
        lab = '記%d–%d' % (ks[0], ks[-1])
    elif cno in SHARED:
        lab = '（與前鈔共用記%d）' % SHARED[cno]
    else:
        lab = '（無記）'
    rows.append((cno, re.sub(r'\\s+', '', it[0])[:34], lab))"""
if old in s and 'SHARED' not in s:
    s = s.replace(old, new)
    io.open(p, 'w', encoding='utf-8').write(s)
    print('patched')
else:
    print('already' if 'SHARED' in s else 'missing')
