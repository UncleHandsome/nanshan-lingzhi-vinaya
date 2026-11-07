import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\mk_pian_split.py'
s = io.open(p, encoding='utf-8').read()
s = s.replace("30: '若下，次聽兼帶'", "30: '題標諸部'")
old = """        ZI[_p - 1] = [(_o[_m.start():].strip(), _rest)] + ZI[_p - 1][1:]"""
new = """        ZI[_p - 1] = [(_o[_m.start():].strip(), _rest)] + ZI[_p - 1][1:]
        if _p == 24:
            _rr = [x for x in _s2(ZI[23][0][1]) if x.strip()]
            while _rr and not any(k in _rr[0] for k in ('導', '能化', '所化')):
                _rr.pop(0)
            if _rr:
                ZI[23] = [(ZI[23][0][0], ''.join(_rr))] + ZI[23][1:]"""
assert old in s
s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8').write(s)
print('p30 marker + p24 tr trim patched')
