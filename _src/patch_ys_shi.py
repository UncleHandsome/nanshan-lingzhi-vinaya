import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\toc_rules.py'
s = io.open(p, encoding='utf-8').read()

s = s.replace("""    if book == 'yeshu':
        # 目次型段落（同時列出多篇）不算篇名""",
"""    if book == 'yeshu':
        if re.match(r'^釋[\\u4e00-\\u9fff]{1,6}篇', t):
            return True
        # 目次型段落（同時列出多篇）不算篇名""")

s = s.replace("""    if book == 'yichao' and t.startswith('將講'):""",
"""    if book == 'yeshu':
        m = re.match(r'^釋([\\u4e00-\\u9fff]{1,6})篇', t)
        if m:
            name = m.group(1)
            MAP = {'受法': '諸戒受法篇第三', '安居': '諸眾安居法篇第六',
                   '懺六聚': '懺六聚法篇第九', '衣藥受淨': '衣藥受淨篇第四',
                   '分衣': '諸分衣法篇第八'}
            return MAP.get(name, name + '篇')
    if book == 'yichao' and t.startswith('將講'):""")
io.open(p, 'w', encoding='utf-8').write(s)
print('yeshu 釋X篇 rule added')
