import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\toc_rules.py'
s = io.open(p, encoding='utf-8').read()
old = """    if book == 'yeshu':
        # 目次型段落（同時列出多篇）不算篇名
        if len(re.findall(r'[\\u4e00-\\u9fff]{2,8}篇第[一二三四五六七八九十]+', t)) >= 2:
            return False"""
new = """    if book == 'yeshu':
        # 目次型段落（同時列出多篇）不算篇名
        if len(re.findall(r'[\\u4e00-\\u9fff]{2,8}篇第[一二三四五六七八九十]+', t)) >= 2:
            return False
        # 篇名段落通常很短；過長的是目次或白話誤植
        if len(re.findall(r'[\\u4e00-\\u9fff]', t)) > 40:
            return False"""
if old in s and '過長的是目次' not in s:
    s = s.replace(old, new)
    io.open(p, 'w', encoding='utf-8').write(s)
    print('length guard added')
else:
    print('already or missing')
