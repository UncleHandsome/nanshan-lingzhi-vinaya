import io, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\mk_p6_huiben.py'
s = io.open(p, encoding='utf-8').read()

# 簽名加 n
s = s.replace("def split_tr(tr, src_parts):", "def split_tr(tr, src_parts, n=0):")
# 呼叫端帶 n
s = s.replace("        ts = split_tr(t, ps)", "        ts = split_tr(t, ps, n)")
# 移除剛才錯誤的 globals 版本
s = s.replace("""SHIFT = {10: -1, 29: -1, 52: +1, 53: +1, 58: -1}
    _sh = SHIFT.get(globals().get('_cur_ji', 0), 0)
    cuts = [max(1, min(c + _sh, len(tr_s) - 1)) for c in cuts]
    cuts = sorted(set(cuts))[:len(src_parts) - 1]""",
"""SHIFT = {10: -1, 29: -1, 52: +1, 53: +1, 58: -1}
    _sh = SHIFT.get(n, 0)
    cuts = [max(1, min(c + _sh, len(tr_s) - 1)) for c in cuts]
    cuts = sorted(set(cuts))[:len(src_parts) - 1]""")
io.open(p, 'w', encoding='utf-8').write(s)
print('split_tr signature + shift by n')
