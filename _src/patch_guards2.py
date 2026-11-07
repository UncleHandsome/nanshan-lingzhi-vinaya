import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\mk_pian_split.py'
s = io.open(p, encoding='utf-8').read()

s = s.replace("if '四分律行事鈔資持記' in _head and ('卷下' in _head or '卷上' in _head or '卷中' in _head):",
              "if _head.startswith('四分律行事鈔資持記') or ('四分律行事鈔資持記' in _head and len(_head) < 40):")
s = s.replace("if _p == 22 and _head.endswith('昭'):\n            _head += '然'",
              "if _p == 22 and '世事昭' in _head and not _head.endswith('昭然'):\n            _head = _head.rstrip('。') + '然'")
io.open(p, 'w', encoding='utf-8').write(s)
print('guards fixed')
