import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\mk_pian_split.py'
s = io.open(p, encoding='utf-8').read()

anchor = "for _p in range(2, len(SECS)):"
add = """BOUND = {22: '題中，上二字', 24: '導，謂能化之法', 28: '沙彌，如注', 30: '若下，次聽兼帶'}
for _p in range(2, len(SECS)):"""
assert anchor in s
s = s.replace(anchor, add, 1)

old = """    _o, _t = ZI[_p - 1][0]
    _m = HDR.search(_o[:160])
    if _m and 4 < _m.start() < 120:"""
new = """    _o, _t = ZI[_p - 1][0]
    _m = None
    if _p in BOUND and BOUND[_p] in _o:
        _k = _o.find(BOUND[_p])
        class _M:
            def __init__(self, k):
                self._k = k
            def start(self):
                return self._k
        _m = _M(_k) if 4 < _k < 120 else None
    if _m is None:
        _m = HDR.search(_o[:160])
    if _m and 4 < _m.start() < 120:"""
assert old in s
s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8').write(s)
print('boundary markers patched')
