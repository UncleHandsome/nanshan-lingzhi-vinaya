import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\mk_pian_split.py'
s = io.open(p, encoding='utf-8').read()
old = """        # 去掉尾巴多帶的「釋X篇」卷頭譯文"""
new = """        # 若頭部譯文吃掉整段，按比例退回一部分
        if _h2(_htr) > 0.85 * max(1, _h2(_t)):
            _ss0 = [x for x in _s2(_t) if x.strip()]
            _cap, _acc = 0.55 * _h2(_t), ''
            for _x in _ss0:
                if _h2(_acc) + _h2(_x) > _cap:
                    break
                _acc += _x
            if _acc:
                _htr = _acc
        # 去掉尾巴多帶的「釋X篇」卷頭譯文"""
assert old in s
s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8').write(s)
print('htr cap patched')
