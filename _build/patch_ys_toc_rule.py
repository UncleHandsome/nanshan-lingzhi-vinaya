import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\toc_rules.py'
s = io.open(p, encoding='utf-8').read()
old = """    if book == 'jieshu':
        if t.startswith('【序】'):
            return True
        if t.startswith('【條目】'):
            return True"""
new = """    if book == 'yeshu':
        # 目次型段落（同時列出多篇）不算篇名
        if len(re.findall(r'[\\u4e00-\\u9fff]{2,8}篇第[一二三四五六七八九十]+', t)) >= 2:
            return False
    if book == 'jieshu':
        if t.startswith('【序】'):
            return True
        if t.startswith('【條目】'):
            return True"""
if old in s and '目次型段落' not in s:
    s = s.replace(old, new)
    io.open(p, 'w', encoding='utf-8').write(s)
    print('yeshu toc rule patched')
else:
    print('already or block missing')
