import os, io, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
for k in ['05a_卷中之一', '05b_卷中之一', '05c_卷中之一']:
    sp = [x.strip() for x in io.open(os.path.join(B, 'TXT_分卷', '01_行事鈔', k + '.txt'), encoding='utf-8').read().split('\n')[5:] if x.strip()]
    tp = os.path.join(B, 'AI語譯', 'out', '01_行事鈔', k + '.txt')
    tt = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(tp, encoding='utf-8').read()) if x.strip()]
    print(k, 'sp', len(sp), 'tt', len(tt))
    for i in range(3):
        print(' ', i, sp[i][:30], '||', tt[i][:30] if i < len(tt) else 'NA')
