import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\toc_rules.py'
s = io.open(p, encoding='utf-8').read()
s = s.replace("""        if re.match(r'^釋[\\u4e00-\\u9fff]{1,6}篇', t2):
            return True""",
"""        if t2 in ('釋受法篇', '釋受法篇。', '釋安居篇', '釋安居篇。',
                  '釋懺六聚篇', '釋懺六聚篇。', '釋衣藥受淨篇', '釋衣藥受淨篇。',
                  '釋分衣篇', '釋分衣篇。'):
            return True""")
io.open(p, 'w', encoding='utf-8').write(s)
print('restricted to known 篇')
