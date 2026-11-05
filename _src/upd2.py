
import io
p = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\README.md'
s = io.open(p, encoding='utf-8').read()
s = s.replace('行事鈔_白話對照本_上卷.pdf | 181', '行事鈔_白話對照本_上卷.pdf | 178')
s = s.replace('行事鈔_白話對照本_下卷.pdf | 223', '行事鈔_白話對照本_下卷.pdf | 220')
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
