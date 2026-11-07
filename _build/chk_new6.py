import io, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
t = io.open(B + r'\合編材料\new.txt', encoding='utf-8').read()
i = t.find('【工作表 6】')
print('定位', i)
seg = t[i:i + 3000]
print(seg[:1200])
