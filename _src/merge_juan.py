
import io
p = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\_src\build_book.py'
s = io.open(p, encoding='utf-8').read()
old = """    for c in chunks:
        j = c['juan'].split('之')[0] if c['juan'] else '全'
        groups.setdefault(j, []).append(c)"""
new = """    for c in chunks:
        j = c['juan'].split('之')[0] if c['juan'] else '全'
        if j == '卷首':
            j = '卷一'
        groups.setdefault(j, []).append(c)"""
assert s.count(old) == 1
s = s.replace(old, new)
# 卷首 chunk 排在最前
s = s.replace("    out = []\n    for f in sorted(os.listdir(S)):", "    out = []\n    files = sorted(os.listdir(S), key=lambda x: (0 if x.startswith('00_') else 1, x))\n    for f in files:")
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
