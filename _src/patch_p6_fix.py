import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\mk_p6_huiben.py'
s = io.open(p, encoding='utf-8').read()

# 1) 記88：合併前兩片（不再切「今準相翻」）
s = s.replace("    88: ['今準相翻', '雜相中', '三法起中'],", "    88: ['雜相中', '三法起中'],")

# 2) PLAN：c50 不再放 88；c51/c52 索引調整
s = s.replace("    49: [(86, 1), (87, 0), (88, 0)],", "    49: [(86, 1), (87, 0), (88, 0)],\n    50: [],")
s = s.replace("    50: [(88, 1)],", "")
s = s.replace("    51: [(88, 2)],", "    51: [(88, 1)],")
s = s.replace("    52: [(88, 3), (89, 0), (90, 0), (91, 0), (92, 0), (93, 0), (94, 0)],",
              "    52: [(88, 2), (89, 0), (90, 0), (91, 0), (92, 0), (93, 0), (94, 0)],")

# 3) 個別譯文位移修正
s = s.replace("cuts = sorted(set(cuts))[:len(src_parts) - 1]",
"""SHIFT = {10: -1, 29: -1, 52: +1, 53: +1, 58: -1}
    _sh = SHIFT.get(globals().get('_cur_ji', 0), 0)
    cuts = [max(1, min(c + _sh, len(tr_s) - 1)) for c in cuts]
    cuts = sorted(set(cuts))[:len(src_parts) - 1]""")
io.open(p, 'w', encoding='utf-8').write(s)
print('88 restructure + shift hooks')
