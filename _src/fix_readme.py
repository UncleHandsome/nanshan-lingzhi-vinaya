
import os, glob, io
base = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
d = os.path.join(base, '白話')
for f in glob.glob(os.path.join(d, '*.png')):
    os.remove(f)
p = os.path.join(base, 'README.md')
s = io.open(p, encoding='utf-8').read()
s = s.replace('書末附校改表 | 33 |', '書末附校改表 | 30 |').replace('只存語譯，供通讀 | 26 |', '只存語譯，供通讀 | 23 |')
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
