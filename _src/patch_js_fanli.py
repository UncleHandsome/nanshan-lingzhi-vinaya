import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\toc_rules.py'
s = io.open(p, encoding='utf-8').read()
old = """    if book == 'jieshu':
        if t.startswith('【序】'):"""
new = """    if book == 'jieshu':
        if t in ('凡例', '目錄', '條目'):
            return True
        if t.startswith('【序】'):"""
if old in s and "t in ('凡例'" not in s:
    s = s.replace(old, new)
    io.open(p, 'w', encoding='utf-8').write(s)
    print('jieshu 凡例/目錄/條目 entries')
else:
    print('already or missing')
