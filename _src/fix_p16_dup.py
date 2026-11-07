import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
fp = B + r'\TXT_分卷\01_行事鈔\08c_卷中之四.txt'
s = io.open(fp, encoding='utf-8').read()
old = '端坐受懺；前人既不行懺者。是非未分。輒為懺主。端坐受懺。前人既不自曉，故請治之。'
new = '端坐受懺；前人既不自曉，故請治之。'
if old in s:
    io.open(fp, 'w', encoding='utf-8').write(s.replace(old, new))
    print('鈔59 衍文已刪')
else:
    print('找不到重複句')
