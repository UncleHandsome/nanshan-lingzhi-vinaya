# -*- coding: utf-8 -*-
import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\mk_pian_split.py'
s = io.open(p, encoding='utf-8').read()

# 移除舊的 p9 預處理
a = s.find('# 篇9 白話前兩段重新切分')
if a > 0:
    b = s.find('_o9, _t9 = ZI[8][0]', a)
    e = s.find('HEADS = {}', b)
    s = s[:a] + s[e:]

# 在 HEADS 之後插入新調整（HEADS 區塊結束於 "FONT = " 之前）
anchor = "FONT = 'SimSun'"
add = '''# 篇9：記1 取 記2 譯文前半（師通多種），記2 取後半
_o1p, _t1p = ZI[8][0]
_o2p, _t2p = ZI[8][1]
_pp = _t2p.find('「資」是取受')
if _pp < 0:
    _pp = _t2p.find('資」是取受')
if _pp > 0:
    _qp = _t2p.find('。', _pp)
    if _qp > 0:
        ZI[8] = [(_o1p, _t2p[:_qp + 1]), (_o2p, _t2p[_qp + 1:])] + ZI[8][2:]

'''
i = s.find(anchor)
assert i > 0
s = s[:i] + add + s[i:]
io.open(p, 'w', encoding='utf-8').write(s)
print('p9 tt fix inserted after HEADS')
