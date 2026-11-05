
import io, os
p = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\README.md'
s = io.open(p, encoding='utf-8').read()
s = s.replace('| 下卷 | 行事鈔_白話對照本_下卷.pdf | 221 | 行事鈔_全白話本_下卷.pdf | 152 |',
              '| 下卷 | 行事鈔_白話對照本_下卷.pdf | 223 | 行事鈔_全白話本_下卷.pdf | 154 |')
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
