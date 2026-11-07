import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\toc_rules.py'
s = io.open(p, encoding='utf-8').read()

s = s.replace("""    if book == 'yeshu':""",
"""    if book == 'yichao' and t.startswith('將講'):
        return True
    if book == 'yeshu':""")

s = s.replace("""    if r.get('label') == 'match':""",
"""    if book == 'yichao' and t.startswith('將講'):
        m = re.match(r'將講(.+?)(?:略存|略以|即以|略)', t)
        return m.group(1) if m else t[2:10]
    if r.get('label') == 'match':""")
io.open(p, 'w', encoding='utf-8').write(s)
print('yichao 將講 rule added')
