import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\mk_pian_split.py'
s = io.open(p, encoding='utf-8').read()

old = """for _p in range(2, len(SECS)):
    _o, _t = ZI[_p - 1][0]
    _m = HDR.search(_o[:160])
    if _m and 4 < _m.start() < 120:
        _head = _o[:_m.start()].strip()
        _ts = _s2(_t)
        _need = _h2(_head)
        _htr = ''
        for _sx in _ts:
            if _h2(_htr) >= _need + 4:
                break
            _htr += _sx
        HEADS[_p] = (_head, _htr)
        _rest = _t[len(_htr):]
        _rest = re.sub(r'^.*?解釋[\\u4e00-\\u9fff]{1,8}篇(?:\\([^)）]*\\))?', '', _rest, count=1)
        ZI[_p - 1] = [(_o[_m.start():].strip(), _rest)] + ZI[_p - 1][1:]"""
new = """for _p in range(2, len(SECS)):
    _o, _t = ZI[_p - 1][0]
    _m = HDR.search(_o[:160])
    if _m and 4 < _m.start() < 120:
        _head = _o[:_m.start()].strip()
        if '四分律行事鈔資持記' in _head and ('卷下' in _head or '卷上' in _head or '卷中' in _head):
            continue          # 卷頭題記，不搬到前篇
        if _p == 22 and _head.endswith('昭'):
            _head += '然'
        _ts = _s2(_t)
        _need = _h2(_head)
        _htr = ''
        for _sx in _ts:
            if _h2(_htr) >= _need + 12:
                break
            _htr += _sx
        # 對齊：若 _t 開頭不是 _htr，找它在前面出現的位置
        if _htr and not _t.startswith(_htr):
            _pos = _t[:400].find(_htr[:12]) if len(_htr) >= 12 else -1
            if _pos > 0:
                _htr = _t[:_pos] + _htr
        HEADS[_p] = (_head, _htr)
        _rest = _t[len(_htr):] if _t.startswith(_htr) else _t
        _rest = re.sub(r'^.*?解釋[\\u4e00-\\u9fff]{1,8}篇(?:\\([^)）]*\\))?', '', _rest, count=1)
        ZI[_p - 1] = [(_o[_m.start():].strip(), _rest)] + ZI[_p - 1][1:]"""
assert old in s, 'HEADS block not found'
s = s.replace(old, new)

s = s.replace("'【記%03d】（續前篇）' % (len(ZI[p - 2]) + 1)", "'【記%03d】（接前文）' % (len(ZI[p - 2]) + 1)")
io.open(p, 'w', encoding='utf-8').write(s)
print('HEADS improved + label 接前文')
