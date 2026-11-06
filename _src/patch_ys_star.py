import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\site_ju.py'
s = io.open(p, encoding='utf-8').read()
old = "        if m3 and m3.start() > 0:"
new = "        o = re.sub(r'\\*+', '', o)\n        if m3 and m3.start() > 0:"
if old in s and "re.sub(r'\\*+'" not in s:
    s = s.replace(old, new, 1)
    io.open(p, 'w', encoding='utf-8').write(s)
    print('asterisk clean')
else:
    print('already or missing')
