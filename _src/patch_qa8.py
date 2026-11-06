# -*- coding: utf-8 -*-
import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\mk_pian_split.py'
s = io.open(p, encoding='utf-8').read()

# 新增 篇8 記26/27 問答縫合
anchor = 'def move_siju():'
add = '''def merge_qa8():
    o26, t26 = ZI[7][25]
    o27, t27 = ZI[7][26]
    k = o27.find('得法中')
    if k <= 0:
        return
    ZI[7][25] = (o26 + o27[:k], t26)
    # 譯文：找到「得法」相關句，切在句號後
    q = t27.find('得法')
    if q > 0:
        qe = t27.find('。', q)
        if qe > 0:
            ZI[7][25] = (o26 + o27[:k], t26 + t27[:qe + 1])
            ZI[7][26] = (o27[k:], t27[qe + 1:])
            return
    ZI[7][26] = (o27[k:], t27)


'''
s = s.replace(anchor, add + anchor, 1)
s = s.replace('''        move_siju()''', '''        merge_qa8()
        move_siju()''')
io.open(p, 'w', encoding='utf-8').write(s)
print('qa8 merge added')
