import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\mk_pian_split.py'
s = io.open(p, encoding='utf-8').read()

old = """        HEADS[_p] = (_head, _htr)"""
new = """        # 去掉尾巴多帶的「釋X篇」卷頭譯文
        _ss = [x for x in _s2(_htr) if x.strip()]
        while len(_ss) > 1:
            _last = _ss[-1]
            if ('篇' in _last and ('釋' in _last or '解釋' in _last)) and len(_last) < 60:
                _ss.pop()
            else:
                break
        _htr = ''.join(_ss)
        HEADS[_p] = (_head, _htr)"""
assert old in s
s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8').write(s)
print('htr trim patched')
