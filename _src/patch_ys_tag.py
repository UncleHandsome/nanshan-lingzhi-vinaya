import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\site_ju.py'
s = io.open(p, encoding='utf-8').read()
old = """            o = sp[i]
            if punct and gi < len(punct) and re.search(r'[，。、；：？！]', punct[gi]):
                o = punct[gi]"""
new = """            o = sp[i]
            if punct and gi < len(punct) and re.search(r'[，。、；：？！]', punct[gi]):
                o = punct[gi]
                mtag = re.match(r'^【[律疏記註]】', sp[i].strip())
                if mtag and '【' not in o[:4]:
                    o = mtag.group(0) + o"""
if old in s and 'mtag' not in s:
    s = s.replace(old, new)
    io.open(p, 'w', encoding='utf-8').write(s)
    print('tag restore patched')
else:
    print('already or missing')
