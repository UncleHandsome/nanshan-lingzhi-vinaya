
import os, glob, io
base = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
d = os.path.join(base, '白話')
for f in glob.glob(os.path.join(d, '*.png')):
    os.remove(f)
p = os.path.join(base, 'README.md')
s = io.open(p, encoding='utf-8').read()
s = s.replace('每節先列原文（楷體、淺底），次列語譯；書末附校改表 | 29 |', '每節先列原文（楷體、淺底），次列語譯 | 28 |')
s = s.replace('只存語譯，供通讀 | 22 |', '只存語譯，供通讀 | 21 |')
s = s.replace('；書末附校改表', '')
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
