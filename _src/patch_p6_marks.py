import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\mk_p6_huiben.py'
s = io.open(p, encoding='utf-8').read()
s = s.replace("    68: ['大界相中', '結示中'],", "    68: ['結示中', '結法中'],")
s = s.replace("    85: ['守護住處'],", "    85: ['解中'],")
s = s.replace("    95: ['不失中'],", "    95: ['棄捨失中'],")
s = s.replace("    98: ['不失中，五種', '不失中'],", "    98: ['不失中'],")
io.open(p, 'w', encoding='utf-8').write(s)
print('marks fixed')
