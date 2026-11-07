import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\hebian_ju.py'
s = io.open(p, encoding='utf-8').read()
s = s.replace("""        if PATS.match(o) or PATS2.match(o):
            continue          # 卷首目次，不當篇名""",
"""        if PATS.match(o) or re.match(r'^\\d+\\s*[\\u4e00-\\u9fff]{2,10}篇', o):
            continue          # 卷首目次，不當篇名""")
io.open(p, 'w', encoding='utf-8').write(s)
print('inline regex patched')
