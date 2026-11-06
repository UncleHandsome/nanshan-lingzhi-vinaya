import io, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\mk_pian_split.py'
s = io.open(p, encoding='utf-8').read()
start = s.find('HEADS = {}')
end = s.find('FONT =', start)
assert start > 0 and end > start
new = '''HEADS = {}
_h2 = lambda x: len(re.findall(r'[\\u4e00-\\u9fff]', x))
_s2 = lambda x: [y for y in re.findall(r'[^。！？；]*[。！？；]?', x) if y.strip()]
for _p in range(2, 11):
    _o, _t = ZI[_p - 1][0]
    _m = HDR.search(_o[:160])
    if _m and _m.start() > 4:
        _head = _o[:_m.start()].strip()
        _k = max(1, int(round(_h2(_head) / max(1, _h2(_o)) * len(_s2(_t)))))
        _ts = _s2(_t)
        _htr = ''.join(_ts[:_k])
        HEADS[_p] = (_head, _htr)
        ZI[_p - 1] = [(_o[_m.start():].strip(), _t[len(_htr):])] + ZI[_p - 1][1:]

'''
s = s[:start] + new + s[end:]
io.open(p, 'w', encoding='utf-8').write(s)
print('HEADS block self-contained')
