import io, os, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
S = os.path.join(B, 'TXT_分卷', '03_業疏')
T = os.path.join(B, 'AI語譯', 'out', '03_業疏')
for k, off in [('04b_卷一之四', 13), ('05a_卷一之五', 17), ('10a_卷二之四', 53)]:
    sp = [x.strip() for x in io.open(os.path.join(S, k + '.txt'), encoding='utf-8').read().split('\n')[5:] if x.strip()]
    tt = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(os.path.join(T, k + '.txt'), encoding='utf-8').read()) if x.strip()]
    print('=====', k, 'off', off)
    for i in range(3):
        j = i + off
        print(' sp%d: %s' % (i, sp[i][:34]))
        print(' tt%d: %s' % (j, tt[j][:34] if j < len(tt) else '—'))
