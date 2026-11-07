import io, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\hebian_ju.py'
s = io.open(p, encoding='utf-8').read()

m = re.search(r'^PATS2=re\.compile\(.*\)\s*$', s, re.M)
if not m:
    print('PATS2 not found')
else:
    line = m.group(0)
    s = s[:m.start()] + s[m.end():]
    # 插到 PATS= 那行後面
    m2 = re.search(r'^PATS=re\.compile\(.*\)\s*$', s, re.M)
    s = s[:m2.end()] + '\n' + line + s[m2.end():]
    io.open(p, 'w', encoding='utf-8').write(s)
    print('moved:', line.strip()[:60])
