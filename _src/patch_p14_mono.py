import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\mk_pian_split.py'
s = io.open(p, encoding='utf-8').read()

old = """    BS = load_bounds(p)
    if BS:"""
new = """    BS = load_bounds(p)
    if BS:
        _last = 1
        _bs2 = []
        for _c, _n in BS:
            _n = max(_n, _last)
            _last = _n
            _bs2.append((_c, _n))
        BS = _bs2"""
assert old in s
s = s.replace(old, new, 1)

old2 = "base = (int(e['base']) if 'base' in e"
new2 = "base = (int(e['base']) if ('base' in e and p != 14)"
assert old2 in s
s = s.replace(old2, new2, 1)
io.open(p, 'w', encoding='utf-8').write(s)
print('patched')
