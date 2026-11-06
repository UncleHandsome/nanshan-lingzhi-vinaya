import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\site2.py'
s = io.open(p, encoding='utf-8').read()

s = s.replace("""                if i2 not in drop_toc and toc_match(bk['out'], o):
                    _lb = toc_label(bk['out'], o)
                    if _lb.startswith('序文：'):""",
"""                if o.startswith('【目錄】') or o.startswith('【條目】'):
                    pass
                elif i2 not in drop_toc and toc_match(bk['out'], o):
                    _lb = toc_label(bk['out'], o)
                    if _lb.startswith('序文：'):""")

s = s.replace("""                if i2 not in drop_toc and toc_match(bk['out'], o):
                    _lb = toc_label(bk['out'], o)
                    if _lb.startswith('序文：'):
                        _lb = '序文'
                    if _lb not in [n for _, n in toc]:""",
"""                if o.startswith('【目錄】') or o.startswith('【條目】'):
                    pass
                elif i2 not in drop_toc and toc_match(bk['out'], o):
                    _lb = toc_label(bk['out'], o)
                    if _lb.startswith('序文：'):
                        _lb = '序文'
                    if _lb not in [n for _, n in toc]:""")
io.open(p, 'w', encoding='utf-8').write(s)
print('skip 目錄/條目 for toc')
