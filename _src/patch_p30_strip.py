import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\mk_pian_split.py'
s = io.open(p, encoding='utf-8').read()
old = """        for _k in range(24, min(28, len(am))):
            am[_k] = 23"""
new = """        for _k in range(24, min(28, len(am))):
            am[_k] = 23
        # 記001 開頭若帶篇29 殘文，切掉
        _o30, _t30 = ZI[29][0]
        _k30 = _o30.find('題標諸部')
        if _k30 > 0:
            _o30 = _o30[_k30:]
        _kt30 = _t30.find('第三十門')
        if _kt30 > 0:
            _t30 = _t30[_kt30:]
        ZI[29] = [(_o30, _t30)] + ZI[29][1:]"""
assert old in s
s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8').write(s)
print('p30 strip patched')
