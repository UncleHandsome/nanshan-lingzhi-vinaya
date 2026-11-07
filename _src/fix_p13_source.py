import io, os, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
# 1) 還原 builder 的 p13 特例
p = os.path.join(B, '_src', 'mk_pian_split.py')
s = io.open(p, encoding='utf-8').read()
a = s.find("    if p == 13:\n        # 卷中之一的譯文")
if a > 0:
    b = s.find("    if p == 30:", a)
    if b < 0:
        b = s.find("    by_c = {}", a)
    s = s[:a] + s[b:]
    io.open(p, 'w', encoding='utf-8').write(s)
    print('p13 special removed')

# 2) 05a 譯文在索引 6 前插入一段（複製索引5），使後續對齊
tp = os.path.join(B, 'AI語譯', 'out', '01_行事鈔', '05a_卷中之一.txt')
tt = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(tp, encoding='utf-8').read()) if x.strip()]
if len(tt) > 6 and '出家脫俗' in tt[6]:
    tt.insert(6, tt[5])
    io.open(tp, 'w', encoding='utf-8').write('\n\n'.join(tt) + '\n')
    print('05a inserted, len', len(tt))
else:
    print('05a unchanged:', tt[6][:20])
