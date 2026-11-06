import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\toc_rules.py'
s = io.open(p, encoding='utf-8').read()

# match：先去掉【疏】【記】前綴
s = s.replace("""    if book == 'yeshu':
        if re.match(r'^釋[\\u4e00-\\u9fff]{1,6}篇', t):
            return True""",
"""    if book == 'yeshu':
        t2 = re.sub(r'^【[疏記]】\\s*', '', t)
        if re.match(r'^釋[\\u4e00-\\u9fff]{1,6}篇', t2):
            return True""")

# label：同樣去前綴
s = s.replace("""    if book == 'yeshu':
        m = re.match(r'^釋([\\u4e00-\\u9fff]{1,6})篇', t)""",
"""    if book == 'yeshu':
        t = re.sub(r'^【[疏記]】\\s*', '', t)
        m = re.match(r'^釋([\\u4e00-\\u9fff]{1,6})篇', t)""")
io.open(p, 'w', encoding='utf-8').write(s)
print('strip tag before match')
