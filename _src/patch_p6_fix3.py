import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\mk_p6_huiben.py'
s = io.open(p, encoding='utf-8').read()
s = s.replace("    SHIFT = {10: -1, 29: -1, 52: +1, 53: +1, 58: -1}",
              "    SHIFT = {10: -1, 29: -1, 52: +1, 53: +1, 58: [0, 1, 0]}")
s = s.replace("""    _sh = SHIFT.get(n, 0)
    cuts = [max(1, min(c + _sh, len(tr_s) - 1)) for c in cuts]""",
"""    _sh = SHIFT.get(n, 0)
    if not isinstance(_sh, list):
        _sh = [_sh] * len(cuts)
    cuts = [max(1, min(c + (_sh[i] if i < len(_sh) else 0), len(tr_s) - 1)) for i, c in enumerate(cuts)]""")
io.open(p, 'w', encoding='utf-8').write(s)
print('per-cut shift')
