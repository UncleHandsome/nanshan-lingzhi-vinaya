import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\site2.py'
s = io.open(p, encoding='utf-8').read()

# 預先計算與頁面建置兩處：戒疏序文只保留第一條
old1 = """                if i2 not in drop_toc and toc_match(bk['out'], o):
                    _lb = toc_label(bk['out'], o)
                    if _lb not in [n for _, n in tt]:
                        tt.append((len(tt) + 1, _lb))"""
new1 = """                if i2 not in drop_toc and toc_match(bk['out'], o):
                    _lb = toc_label(bk['out'], o)
                    if _lb.startswith('序文：'):
                        _lb = '序文'
                    if _lb not in [n for _, n in tt]:
                        tt.append((len(tt) + 1, _lb))"""
if old1 in s:
    s = s.replace(old1, new1)

old2 = """                if i2 not in drop_toc and toc_match(bk['out'], o):
                    _lb = toc_label(bk['out'], o)
                    if _lb not in [n for _, n in toc]:"""
new2 = """                if i2 not in drop_toc and toc_match(bk['out'], o):
                    _lb = toc_label(bk['out'], o)
                    if _lb.startswith('序文：'):
                        _lb = '序文'
                    if _lb not in [n for _, n in toc]:"""
if old2 in s:
    s = s.replace(old2, new2)
io.open(p, 'w', encoding='utf-8').write(s)
print('jieshu 序文 collapsed')
