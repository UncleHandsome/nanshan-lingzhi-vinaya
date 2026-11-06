import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\mk_xml_huiben.py'
s = io.open(p, encoding='utf-8').read()

s = s.replace("""han = lambda s: ''.join(re.findall(r'[\\u4e00-\\u9fff]', s))""",
"""han0 = lambda s: ''.join(re.findall(r'[\\u4e00-\\u9fff]', s))
VAR = {'說': '説', '眾': '衆', '為': '爲', '教': '敎', '即': '卽', '既': '旣',
       '並': '竝', '床': '牀', '收': '収', '煮': '煑', '查': '査'}
han = lambda s: ''.join(VAR.get(c, c) for c in han0(s))""")

s = s.replace("""    H, pos2p = '', []
    for i, t in enumerate(ch):
        for c in han(t):
            H += c; pos2p.append(i)""",
"""    H, pos2p = '', []
    for i, t in enumerate(ch):
        for c in han(t):
            H += c; pos2p.append(i)""")
io.open(p, 'w', encoding='utf-8').write(s)
print('variant normalization added')
