import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\site2.py'
s = io.open(p, encoding='utf-8').read()

old = """                    if _lb.startswith('序文：'):
                        _lb = '序文'
                    if _lb not in [n for _, n in toc]:"""
new = """                    if _lb.startswith('序文：'):
                        _lb = '序文'
                    if bk['out'] == 'jieshu' and v in ('卷一', '卷一上') and _lb not in ('序文', '凡例', '目錄', '條目'):
                        _lb = ''
                    if _lb and _lb not in [n for _, n in toc]:"""
if old in s and "and _lb not in ('序文'" not in s:
    s = s.replace(old, new)
    io.open(p, 'w', encoding='utf-8').write(s)
    print('卷一 filter patched')
else:
    print('already or missing')
