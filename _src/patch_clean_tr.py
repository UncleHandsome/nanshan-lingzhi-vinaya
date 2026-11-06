import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\mk_pian_split.py'
s = io.open(p, encoding='utf-8').read()
old = """        _lead = ''
        _zt = zt"""
new = """        _lead = ''
        _zt = clean_tr(zt)"""
assert old in s
s = s.replace(old, new)
io.open(p, 'w', encoding='utf-8').write(s)
print('emit clean_tr added')
