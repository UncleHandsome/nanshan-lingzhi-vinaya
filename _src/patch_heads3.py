import io, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\mk_pian_split.py'
s = io.open(p, encoding='utf-8').read()
old = "        ZI[_p - 1] = [(_o[_m.start():].strip(), _t[len(_htr):])] + ZI[_p - 1][1:]"
new = """        _rest = _t[len(_htr):]
        _rest = re.sub(r'^.*?解釋[\\u4e00-\\u9fff]{1,8}篇(?:\\([^)）]*\\))?', '', _rest, count=1)
        ZI[_p - 1] = [(_o[_m.start():].strip(), _rest)] + ZI[_p - 1][1:]"""
if old in s:
    s = s.replace(old, new)
    io.open(p, 'w', encoding='utf-8').write(s)
    print('tail translation cleanup added')
else:
    print('missing')
