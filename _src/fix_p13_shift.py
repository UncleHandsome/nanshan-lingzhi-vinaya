import io, os, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
tp = os.path.join(B, 'AI語譯', 'out', '01_行事鈔', '05a_卷中之一.txt')
tt = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(tp, encoding='utf-8').read()) if x.strip()]
new = [tt[0]] + tt[:-1]
io.open(tp, 'w', encoding='utf-8').write('\n\n'.join(new) + '\n')
print('05a 譯文右移一格，len', len(new))
